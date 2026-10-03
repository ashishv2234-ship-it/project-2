from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(50), nullable=False, index=True) # LANDSLIDE_WARNING, FLASH_FLOOD_SURGE, BRIDGE_CLOSURE, MONSOON_RED_ALERT, CONVOY_STALLED
    severity = Column(String(30), nullable=False, default="HIGH", index=True) # LOW, MODERATE, HIGH, CRITICAL
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    road_id = Column(String(36), ForeignKey("roads.id"), nullable=True, index=True)
    location_desc = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(30), default="ACTIVE", index=True) # ACTIVE, ACKNOWLEDGED, RESOLVED, EXPIRED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    expires_at = Column(DateTime, nullable=True)

    notifications = relationship("Notification", back_populates="alert")

class AlertSubscription(Base):
    __tablename__ = "alert_subscriptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    channels_json = Column(Text, default='["WEBSOCKET", "PUSH", "SMS"]') # JSON array
    districts_json = Column(Text, default='["all"]') # JSON array of district IDs
    alert_types_json = Column(Text, default='["all"]') # JSON array
    language = Column(String(20), default="en")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    alert_id = Column(String(36), ForeignKey("alerts.id"), nullable=True, index=True)
    channel = Column(String(30), default="WEBSOCKET") # WEBSOCKET, PUSH, SMS, WHATSAPP, EMAIL
    language = Column(String(20), default="en") # en, as, bn, mni, lus, kha, grt, nag, hi
    message_text = Column(Text, nullable=False)
    status = Column(String(30), default="SENT") # PENDING, SENT, DELIVERED, READ, FAILED
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    read_at = Column(DateTime, nullable=True)

    alert = relationship("Alert", back_populates="notifications")

class EmergencyEvent(Base):
    __tablename__ = "emergency_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. EM-MONSOON-SURGE-L3
    title = Column(String(150), nullable=False)
    type = Column(String(50), default="MONSOON_SURGE") # CYCLONE_REMAL, FLASH_FLOOD, MASS_LANDSLIDE, EARTHQUAKE
    level = Column(String(20), default="LEVEL_3") # LEVEL_1, LEVEL_2, LEVEL_3_CATASTROPHIC
    affected_districts_json = Column(Text, nullable=False) # JSON array of district names/IDs
    activated_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    end_time = Column(DateTime, nullable=True)
    priority_corridors_json = Column(Text, nullable=False) # JSON array e.g. ["NH-27", "NH-6", "NH-102"]
    is_active = Column(Boolean, default=True)
