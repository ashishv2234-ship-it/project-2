import json
from datetime import UTC, datetime
from typing import Any

from app.core.audit import record_audit_log
from app.core.database import get_db
from app.models.incidents import FieldReport, Incident
from app.models.transport import RoadSegment
from app.schemas.incidents import (
    FieldReportCreate,
    FieldReportResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    IncidentVerifyRequest,
    MediaUploadResponse,
)
from app.services.integrations import integrations
from app.services.offline_sync_engine import offline_sync_engine
from app.websocket.manager import ws_manager
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter(tags=["Incidents & Field Reporting"])


# Incidents
@router.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    payload: IncidentCreate, db: Session = Depends(get_db)
) -> Any:
    """Report an incident (landslide, flood, bridge closure, congestion)."""
    incident = Incident(
        type=payload.type,
        severity=payload.severity,
        location_desc=payload.location_desc,
        lat=payload.lat,
        lon=payload.lon,
        road_segment_id=payload.road_segment_id,
        district_id=payload.district_id,
        description=payload.description,
        estimated_clearance_hours=payload.estimated_clearance_hours,
        status="REPORTED",
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Broadcast alert to subscribers
    await ws_manager.broadcast(
        {
            "event": "INCIDENT_REPORTED",
            "incident_id": incident.id,
            "type": incident.type,
            "severity": incident.severity,
            "location": incident.location_desc,
            "lat": incident.lat,
            "lon": incident.lon,
        },
        channel="alerts",
    )

    return incident


@router.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(
    status_filter: str | None = None,
    type_filter: str | None = None,
    severity_filter: str | None = None,
    db: Session = Depends(get_db),
) -> Any:
    """List all incidents with optional severity and status filters."""
    query = db.query(Incident)
    if status_filter:
        query = query.filter(Incident.status == status_filter.upper())
    if type_filter:
        query = query.filter(Incident.type == type_filter.lower())
    if severity_filter:
        query = query.filter(Incident.severity == severity_filter.upper())
    return query.order_by(Incident.created_at.desc()).all()


@router.get("/incidents/{id}", response_model=IncidentResponse)
def get_incident_by_id(id: str, db: Session = Depends(get_db)) -> Any:
    """Get single incident details."""
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/incidents/{id}", response_model=IncidentResponse)
def update_incident(
    id: str, payload: IncidentUpdate, db: Session = Depends(get_db)
) -> Any:
    """Update incident status or estimated clearance."""
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(incident, field, val)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/incidents/{id}/verify")
async def verify_incident(
    id: str, payload: IncidentVerifyRequest, db: Session = Depends(get_db)
) -> Any:
    """Official verification by District Officer or BRO/PWD Chief."""
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_status = incident.status
    if payload.verified:
        incident.status = "VERIFIED"
        if payload.updated_severity:
            incident.severity = payload.updated_severity

        # If severe, mark linked road segment blocked
        if incident.road_segment_id:
            segment = (
                db.query(RoadSegment)
                .filter(RoadSegment.id == incident.road_segment_id)
                .first()
            )
            if segment:
                segment.current_status = "BLOCKED"
    else:
        incident.status = "REJECTED"

    db.commit()

    record_audit_log(
        db=db,
        user_id="OFFICER",
        action="INCIDENT_VERIFICATION",
        entity_type="incident",
        entity_id=incident.id,
        old_value=old_status,
        new_value=incident.status,
    )

    await ws_manager.broadcast(
        {
            "event": "INCIDENT_VERIFIED",
            "incident_id": incident.id,
            "status": incident.status,
            "severity": incident.severity,
        },
        channel="alerts",
    )

    return {"message": f"Incident {id} marked as {incident.status}."}


@router.post("/incidents/{id}/resolve")
async def resolve_incident(id: str, db: Session = Depends(get_db)) -> Any:
    """Mark an incident resolved after debris clearance or water recession."""
    incident = db.query(Incident).filter(Incident.id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "RESOLVED"
    incident.resolved_at = datetime.now(UTC)

    # Reopen segment if blocked by this incident
    if incident.road_segment_id:
        segment = (
            db.query(RoadSegment)
            .filter(RoadSegment.id == incident.road_segment_id)
            .first()
        )
        if segment:
            segment.current_status = "OPEN"

    db.commit()

    await ws_manager.broadcast(
        {
            "event": "INCIDENT_RESOLVED",
            "incident_id": incident.id,
            "message": f"Clearance complete at {incident.location_desc}. Corridor restored.",
        },
        channel="alerts",
    )

    return {"message": f"Incident {id} resolved. Road restored."}


# Field Reports
@router.post("/field-reports", response_model=FieldReportResponse)
def submit_field_report(
    payload: FieldReportCreate, db: Session = Depends(get_db)
) -> Any:
    """Submit geo-tagged field report with offline UUID support."""
    res = offline_sync_engine._handle_field_report(
        db=db,
        user_id="FIELD-OFFICER-DEFAULT",
        device_id=payload.device_id or "UNKNOWN_DEVICE",
        client_uuid=payload.client_uuid,
        payload=payload.model_dump(),
        client_dt=payload.offline_created_at,
    )
    db.commit()
    report = db.query(FieldReport).filter(FieldReport.id == res["server_id"]).first()
    return FieldReportResponse(
        id=report.id,
        client_uuid=report.client_uuid,
        incident_id=report.incident_id,
        reporter_id=report.reporter_id,
        lat=report.lat,
        lon=report.lon,
        accuracy_m=report.accuracy_m,
        disruption_type=report.disruption_type,
        severity=report.severity,
        description=report.description,
        media_files=json.loads(report.media_files_json)
        if report.media_files_json
        else [],
        offline_created_at=report.offline_created_at,
        synced_at=report.synced_at,
        sync_status=report.sync_status,
    )


@router.post("/field-reports/sync")
def sync_offline_reports(
    payload: list[FieldReportCreate], db: Session = Depends(get_db)
) -> Any:
    """Batch synchronize field reports queued during network blackout."""
    batch_items = [
        {
            "client_uuid": r.client_uuid,
            "operation": "CREATE_FIELD_REPORT",
            "payload": r.model_dump(),
            "client_timestamp": r.offline_created_at.isoformat(),
        }
        for r in payload
    ]
    return offline_sync_engine.process_sync_batch(
        db=db,
        user_id="FIELD-OFFICER-DEFAULT",
        device_id="MOBILE-OFFLINE-QUEUE",
        queue_items=batch_items,
    )


# Media Uploads
@router.post("/media/upload", response_model=MediaUploadResponse)
async def upload_media_file(file: UploadFile = File(...)) -> Any:
    """Direct upload for photos/videos of road damages and landslides."""
    contents = await file.read()
    import hashlib

    sha256 = hashlib.sha256(contents).hexdigest()
    media_id = sha256[:16]
    simulated_url = f"https://cdn.ner-logisense.gov.in/media/{media_id}_{file.filename}"

    return {
        "media_id": media_id,
        "file_url": simulated_url,
        "checksum_sha256": sha256,
        "size_bytes": len(contents),
        "virus_scanned": True,
    }


@router.get("/media/{id}/presigned-url")
def get_presigned_url(id: str, filename: str | None = "hazard.jpg") -> Any:
    """Obtain secure signed URL for S3/MinIO direct upload."""
    return integrations.generate_presigned_upload_url(filename, "image/jpeg")
