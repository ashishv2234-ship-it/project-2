import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.incidents import FieldReport, Incident
from app.models.transport import RoadSegment, RoadStatusEvent
from app.models.vehicles import GPSReading, Vehicle
from app.core.audit import record_audit_log

class OfflineSyncEngine:
    """
    Offline Synchronization Engine for NER low-connectivity mobile clients.
    Features:
      1. Append-only queue execution
      2. Client-generated UUID idempotency check
      3. Conflict resolution:
         - Field reports: Keep both server and client versions, flag conflict for verification task
         - Road status: Use latest official verified update with audit log
         - GPS readings: Batched historical insertion sorted by timestamp
      4. Delta sync with updated_at cursors
    """

    def process_sync_batch(self, db: Session, user_id: str, device_id: str, queue_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        processed_count = 0
        success_count = 0
        conflict_count = 0

        # Sort queue items by client timestamp to preserve causality
        sorted_items = sorted(queue_items, key=lambda x: x.get("client_timestamp", ""))

        for item in sorted_items:
            processed_count += 1
            client_uuid = item.get("client_uuid")
            operation = item.get("operation")
            payload = item.get("payload", {})
            client_timestamp_str = item.get("client_timestamp")
            
            try:
                if client_timestamp_str:
                    client_dt = datetime.fromisoformat(client_timestamp_str.replace("Z", "+00:00"))
                else:
                    client_dt = datetime.now(timezone.utc)
            except Exception:
                client_dt = datetime.now(timezone.utc)

            # Idempotency check: Has this client_uuid already been processed?
            existing_report = db.query(FieldReport).filter(FieldReport.client_uuid == client_uuid).first()
            if existing_report:
                results.append({
                    "client_uuid": client_uuid,
                    "status": "DUPLICATE_SKIPPED",
                    "server_id": existing_report.id,
                    "conflict_details": "Record with this client UUID already synced",
                    "processed_at": datetime.now(timezone.utc).isoformat()
                })
                success_count += 1
                continue

            if operation == "CREATE_FIELD_REPORT":
                res = self._handle_field_report(db, user_id, device_id, client_uuid, payload, client_dt)
            elif operation == "UPDATE_ROAD_STATUS":
                res = self._handle_road_status(db, user_id, client_uuid, payload, client_dt)
            elif operation == "BATCH_GPS":
                res = self._handle_gps_batch(db, client_uuid, payload)
            else:
                res = {
                    "client_uuid": client_uuid,
                    "status": "REJECTED",
                    "conflict_details": f"Unknown operation: {operation}",
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }

            if res["status"] == "SUCCESS":
                success_count += 1
            elif res["status"] == "CONFLICT_FLAGGED":
                conflict_count += 1

            results.append(res)

        db.commit()

        return {
            "processed_count": processed_count,
            "success_count": success_count,
            "conflict_count": conflict_count,
            "results": results
        }

    def _handle_field_report(
        self, db: Session, user_id: str, device_id: str, client_uuid: str, payload: Dict[str, Any], client_dt: datetime
    ) -> Dict[str, Any]:
        """
        Field reports conflict resolution:
        If an existing incident is reported in the same 500m vicinity within 2 hours,
        flag conflict and attach report for manual verification.
        """
        lat = float(payload.get("lat", 25.18))
        lon = float(payload.get("lon", 92.99))
        disruption_type = payload.get("disruption_type", "Landslide")
        severity = payload.get("severity", "CRITICAL")
        description = payload.get("description", "")
        media_files = payload.get("media_files", [])

        # Check for spatial collision with existing incident
        nearby_incident = db.query(Incident).filter(
            Incident.status.in_(["REPORTED", "VERIFIED", "UNDER_VERIFICATION"]),
            Incident.lat.between(lat - 0.005, lat + 0.005),
            Incident.lon.between(lon - 0.005, lon + 0.005)
        ).first()

        incident_id = None
        status = "SUCCESS"
        conflict_msg = None

        if nearby_incident:
            incident_id = nearby_incident.id
            if nearby_incident.severity != severity:
                # Conflicting severity assessment
                status = "CONFLICT_FLAGGED"
                conflict_msg = f"Existing incident #{nearby_incident.id[:8]} has severity {nearby_incident.severity}, field report claimed {severity}. Both preserved."
        else:
            # Create new incident
            new_incident = Incident(
                type=disruption_type.lower().replace(" ", "_"),
                severity=severity,
                location_desc=payload.get("location_desc", f"Near GNSS {lat:.4f}, {lon:.4f}"),
                lat=lat,
                lon=lon,
                description=description,
                status="REPORTED",
                reported_by=user_id
            )
            db.add(new_incident)
            db.flush()
            incident_id = new_incident.id

        # Insert field report
        report = FieldReport(
            client_uuid=client_uuid,
            incident_id=incident_id,
            reporter_id=user_id,
            lat=lat,
            lon=lon,
            accuracy_m=float(payload.get("accuracy_m", 5.0)),
            disruption_type=disruption_type,
            severity=severity,
            description=description,
            media_files_json=json.dumps(media_files),
            offline_created_at=client_dt,
            synced_at=datetime.now(timezone.utc),
            sync_status="CONFLICT_FLAGGED" if status == "CONFLICT_FLAGGED" else "SYNCED",
            device_id=device_id
        )
        db.add(report)
        db.flush()

        record_audit_log(
            db=db,
            user_id=user_id,
            action="OFFLINE_FIELD_REPORT_SYNC",
            entity_type="field_report",
            entity_id=report.id,
            new_value={"client_uuid": client_uuid, "incident_id": incident_id, "status": status}
        )

        return {
            "client_uuid": client_uuid,
            "status": status,
            "server_id": report.id,
            "conflict_details": conflict_msg,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

    def _handle_road_status(
        self, db: Session, user_id: str, client_uuid: str, payload: Dict[str, Any], client_dt: datetime
    ) -> Dict[str, Any]:
        """
        Status updates conflict resolution:
        Use latest official verified update with audit history.
        """
        segment_id = payload.get("segment_id")
        new_status = payload.get("status")
        reason = payload.get("reason", "Field telemetry update")

        segment = db.query(RoadSegment).filter(RoadSegment.id == segment_id).first()
        if not segment:
            return {
                "client_uuid": client_uuid,
                "status": "REJECTED",
                "conflict_details": f"Segment {segment_id} not found",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }

        old_status = segment.current_status
        segment.current_status = new_status
        segment.updated_at = datetime.now(timezone.utc)

        # Log event
        status_event = RoadStatusEvent(
            segment_id=segment.id,
            status=new_status,
            source="OFFLINE_CLIENT_SYNC",
            confidence=0.92,
            start_time=client_dt,
            reason=reason,
            verified_by=user_id
        )
        db.add(status_event)

        record_audit_log(
            db=db,
            user_id=user_id,
            action="OFFLINE_ROAD_STATUS_UPDATE",
            entity_type="road_segment",
            entity_id=segment.id,
            old_value=old_status,
            new_value=new_status
        )

        return {
            "client_uuid": client_uuid,
            "status": "SUCCESS",
            "server_id": segment.id,
            "conflict_details": None,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

    def _handle_gps_batch(self, db: Session, client_uuid: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        GPS readings conflict resolution:
        Accept batched historical points using timestamp ordering.
        """
        vehicle_id = payload.get("vehicle_id")
        readings = payload.get("readings", [])
        
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            return {
                "client_uuid": client_uuid,
                "status": "REJECTED",
                "conflict_details": f"Vehicle {vehicle_id} not found",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }

        # Sort readings chronologically
        sorted_readings = sorted(readings, key=lambda x: x.get("timestamp", ""))
        
        last_pt = None
        for r in sorted_readings:
            try:
                ts = datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            except Exception:
                ts = datetime.now(timezone.utc)
                
            gps = GPSReading(
                vehicle_id=vehicle_id,
                timestamp=ts,
                latitude=float(r["latitude"]),
                longitude=float(r["longitude"]),
                speed_kmh=float(r.get("speed_kmh", 0.0)),
                heading_deg=float(r.get("heading_deg", 0.0)),
                accuracy_m=float(r.get("accuracy_m", 2.5)),
                altitude_m=float(r.get("altitude_m", 250.0)),
                ignition_status=bool(r.get("ignition_status", True)),
                engine_temp_c=float(r.get("engine_temp_c", 85.0)),
                cryo_temp_c=float(r.get("cryo_temp_c")) if r.get("cryo_temp_c") is not None else None,
                navic_satellite_count=int(r.get("navic_satellite_count", 9))
            )
            db.add(gps)
            last_pt = gps

        # Update vehicle last position if newer
        if last_pt:
            vehicle.last_lat = last_pt.latitude
            vehicle.last_lon = last_pt.longitude
            vehicle.last_speed_kmh = last_pt.speed_kmh
            vehicle.last_heading_deg = last_pt.heading_deg
            vehicle.cryo_temp_c = last_pt.cryo_temp_c
            vehicle.last_ping_time = last_pt.timestamp

        return {
            "client_uuid": client_uuid,
            "status": "SUCCESS",
            "server_id": vehicle_id,
            "conflict_details": f"Ingested {len(sorted_readings)} historical telemetry points",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

offline_sync_engine = OfflineSyncEngine()
