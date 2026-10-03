from typing import Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.transport import Road, RoadSegment
from app.models.incidents import Incident
from app.models.alerts import Alert
from app.models.vehicles import Vehicle
from app.schemas.offline_sync import (
    SyncBatchRequest, SyncBatchResponse, DeltaSyncResponse
)
from app.services.offline_sync_engine import offline_sync_engine

router = APIRouter(prefix="/sync", tags=["Offline-First Synchronization"])

@router.post("/queue", response_model=SyncBatchResponse)
def sync_offline_queue(payload: SyncBatchRequest, db: Session = Depends(get_db)) -> Any:
    """
    Synchronize batched offline queue items:
    - Guarantees idempotency via client_uuid
    - Implements conflict resolution
    - Preserves causal order
    """
    queue_dicts = [item.model_dump() for item in payload.queue_items]
    res = offline_sync_engine.process_sync_batch(
        db=db,
        user_id="OFFLINE-CLIENT",
        device_id=payload.device_id,
        queue_items=queue_dicts
    )
    return {
        "sync_session_id": payload.sync_session_id,
        "processed_count": res["processed_count"],
        "success_count": res["success_count"],
        "conflict_count": res["conflict_count"],
        "results": res["results"]
    }

@router.get("/delta", response_model=DeltaSyncResponse)
def get_delta_sync(
    last_synced_at: Optional[str] = Query(None, description="ISO timestamp cursor from previous sync"),
    district: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Provides delta synchronization using updated_at cursor.
    Allows mobile clients to fetch only entities modified since last synchronization.
    """
    cursor_dt = None
    if last_synced_at:
        try:
            cursor_dt = datetime.fromisoformat(last_synced_at.replace("Z", "+00:00"))
        except Exception:
            cursor_dt = None

    roads = db.query(Road).all()
    segments = db.query(RoadSegment)
    if cursor_dt:
        segments = segments.filter(RoadSegment.updated_at >= cursor_dt)
    segments_list = segments.all()

    incidents = db.query(Incident).filter(Incident.status.in_(["REPORTED", "VERIFIED", "IN_CLEARANCE"]))
    if cursor_dt:
        incidents = incidents.filter(Incident.created_at >= cursor_dt)
    
    alerts = db.query(Alert).filter(Alert.status == "ACTIVE")
    if cursor_dt:
        alerts = alerts.filter(Alert.created_at >= cursor_dt)

    vehicles = db.query(Vehicle).all()

    return {
        "server_timestamp": datetime.now(timezone.utc),
        "updated_roads": [{"id": r.id, "name": r.name, "code": r.code, "status": r.status} for r in roads],
        "updated_segments": [
            {
                "id": s.id,
                "status": s.current_status,
                "delay_min": s.expected_delay_min,
                "slide_risk": s.landslide_risk_score,
                "flood_risk": s.flood_risk_score
            } for s in segments_list
        ],
        "active_incidents": [
            {
                "id": i.id,
                "type": i.type,
                "severity": i.severity,
                "location": i.location_desc,
                "lat": i.lat,
                "lon": i.lon,
                "status": i.status
            } for i in incidents.all()
        ],
        "active_alerts": [
            {
                "id": a.id,
                "type": a.type,
                "severity": a.severity,
                "message": a.message,
                "location": a.location_desc
            } for a in alerts.all()
        ],
        "active_convoys": [
            {
                "id": v.id,
                "registration": v.registration_number,
                "type": v.type,
                "lat": v.last_lat,
                "lon": v.last_lon,
                "speed_kmh": v.last_speed_kmh,
                "cryo_temp_c": v.cryo_temp_c
            } for v in vehicles
        ]
    }
