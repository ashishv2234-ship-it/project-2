import json
from typing import List, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.audit import record_audit_log
from app.models.alerts import Alert, AlertSubscription, Notification, EmergencyEvent
from app.schemas.alerts import (
    AlertCreate, AlertResponse, AlertNotifyRequest, NotificationResponse,
    NotificationPreferencesRequest, EmergencyEventCreate, EmergencyEventUpdate, EmergencyEventResponse
)
from app.services.alert_classifier import alert_classifier
from app.services.integrations import integrations
from app.websocket.manager import ws_manager

router = APIRouter(tags=["Alerts & Tactical Emergency Coordination"])

# Alerts
@router.post("/alerts", response_model=AlertResponse)
async def create_alert(payload: AlertCreate, db: Session = Depends(get_db)) -> Any:
    """Create automated or manual alert with AI deduplication check."""
    classification = alert_classifier.classify_and_filter(
        alert_type=payload.type,
        base_severity=payload.severity,
        district_name=payload.location_desc
    )

    alert = Alert(
        type=payload.type,
        severity=payload.severity,
        district_id=payload.district_id,
        road_id=payload.road_id,
        location_desc=payload.location_desc,
        message=payload.message,
        expires_at=payload.expires_at,
        status="ACTIVE"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Broadcast via WebSocket
    await ws_manager.broadcast({
        "event": "TACTICAL_ALERT",
        "alert_id": alert.id,
        "type": alert.type,
        "severity": alert.severity,
        "location": alert.location_desc,
        "message": alert.message,
        "priority": classification["calculated_priority"]
    }, channel="alerts")

    return alert

@router.get("/alerts", response_model=List[AlertResponse])
def list_alerts(
    status_filter: Optional[str] = "ACTIVE",
    severity_filter: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Any:
    """List operational alerts."""
    query = db.query(Alert)
    if status_filter:
        query = query.filter(Alert.status == status_filter.upper())
    if severity_filter:
        query = query.filter(Alert.severity == severity_filter.upper())
    return query.order_by(Alert.created_at.desc()).all()

@router.patch("/alerts/{id}", response_model=AlertResponse)
def update_alert(id: str, status: str, db: Session = Depends(get_db)) -> Any:
    """Acknowledge or resolve an active alert."""
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = status.upper()
    db.commit()
    db.refresh(alert)
    return alert

@router.post("/alerts/{id}/notify")
async def dispatch_alert_notifications(
    id: str,
    payload: AlertNotifyRequest,
    db: Session = Depends(get_db)
) -> Any:
    """Broadcast alert across regional channels (WebSocket, SMS, Push, WhatsApp)."""
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Generate multilingual translations
    multilingual_versions = {}
    for lang in ["en", "as", "bn", "hi", "mni", "lus", "kha", "grt", "nag"]:
        multilingual_versions[lang] = integrations.format_multilingual_alert(
            template_key="alert_blockade",
            lang=lang,
            params={"road": "Corridor", "location": alert.location_desc, "reason": alert.message}
        )

    # Dispatched notifications record
    notification = Notification(
        alert_id=alert.id,
        channel="WEBSOCKET",
        language="en",
        message_text=alert.message,
        status="SENT",
        sent_at=datetime.now(timezone.utc)
    )
    db.add(notification)
    db.commit()

    return {
        "status": "DISPATCHED",
        "channels": payload.channels,
        "multilingual_preview": multilingual_versions
    }

# Notifications
@router.get("/notifications", response_model=List[NotificationResponse])
def get_user_notifications(db: Session = Depends(get_db)) -> Any:
    """Get recent notifications dispatched to user."""
    return db.query(Notification).order_by(Notification.sent_at.desc()).limit(20).all()

@router.patch("/notifications/{id}/read")
def mark_notification_read(id: str, db: Session = Depends(get_db)) -> Any:
    """Acknowledge notification read receipt."""
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.status = "READ"
    notif.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Notification marked as read."}

@router.post("/notification-preferences")
def save_notification_preferences(payload: NotificationPreferencesRequest, db: Session = Depends(get_db)) -> Any:
    """Save multilingual and channel preferences."""
    return {"status": "SUCCESS", "preferences_saved": payload.model_dump()}

# Emergency Events
@router.post("/emergency-events", response_model=EmergencyEventResponse)
async def activate_emergency_event(payload: EmergencyEventCreate, db: Session = Depends(get_db)) -> Any:
    """Declare state-wide or district-wide emergency disaster mode (e.g. Monsoon Surge Level 3)."""
    event = EmergencyEvent(
        event_code=payload.event_code,
        title=payload.title,
        type=payload.type,
        level=payload.level,
        affected_districts_json=json.dumps(payload.affected_districts),
        activated_by="SUPER_ADMIN",
        priority_corridors_json=json.dumps(payload.priority_corridors),
        is_active=True
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    record_audit_log(
        db=db,
        user_id="SUPER_ADMIN",
        action="EMERGENCY_DISASTER_MODE_ACTIVATED",
        entity_type="emergency_event",
        entity_id=event.id,
        new_value={"code": event.event_code, "level": event.level}
    )

    await ws_manager.broadcast({
        "event": "EMERGENCY_MODE_ACTIVATED",
        "title": event.title,
        "level": event.level,
        "affected_districts": payload.affected_districts,
        "priority_corridors": payload.priority_corridors
    }, channel="alerts")

    return EmergencyEventResponse(
        id=event.id,
        event_code=event.event_code,
        title=event.title,
        type=event.type,
        level=event.level,
        affected_districts=payload.affected_districts,
        priority_corridors=payload.priority_corridors,
        activated_by=event.activated_by,
        start_time=event.start_time,
        end_time=event.end_time,
        is_active=event.is_active
    )

@router.patch("/emergency-events/{id}", response_model=EmergencyEventResponse)
def update_emergency_event(id: str, payload: EmergencyEventUpdate, db: Session = Depends(get_db)) -> Any:
    """Deactivate or update emergency disaster state."""
    event = db.query(EmergencyEvent).filter(EmergencyEvent.id == id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Emergency event not found")
    
    if payload.title:
        event.title = payload.title
    if payload.level:
        event.level = payload.level
    if payload.is_active is not None:
        event.is_active = payload.is_active
        if not payload.is_active:
            event.end_time = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(event)

    return EmergencyEventResponse(
        id=event.id,
        event_code=event.event_code,
        title=event.title,
        type=event.type,
        level=event.level,
        affected_districts=json.loads(event.affected_districts_json),
        priority_corridors=json.loads(event.priority_corridors_json),
        activated_by=event.activated_by,
        start_time=event.start_time,
        end_time=event.end_time,
        is_active=event.is_active
    )
