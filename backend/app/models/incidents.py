import uuid
from datetime import UTC, datetime

from app.core.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(
        String(50), nullable=False, index=True
    )  # landslide, flood, road_damage, bridge_closure, accident, congestion, vehicle_breakdown
    severity = Column(
        String(30), nullable=False, default="HIGH", index=True
    )  # LOW, MODERATE, HIGH, CRITICAL
    location_desc = Column(String(200), nullable=False)
    lat = Column(Float, nullable=False, index=True)
    lon = Column(Float, nullable=False, index=True)
    road_segment_id = Column(
        String(36), ForeignKey("road_segments.id"), nullable=True, index=True
    )
    district_id = Column(
        String(36), ForeignKey("districts.id"), nullable=True, index=True
    )
    description = Column(Text, nullable=False)
    status = Column(
        String(30), default="REPORTED", index=True
    )  # REPORTED, UNDER_VERIFICATION, VERIFIED, IN_CLEARANCE, RESOLVED, REJECTED
    reported_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    verified_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    estimated_clearance_hours = Column(Float, default=4.0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    resolved_at = Column(DateTime, nullable=True)

    field_reports = relationship("FieldReport", back_populates="incident")
    verification_tasks = relationship("VerificationTask", back_populates="incident")


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_uuid = Column(
        String(64), unique=True, index=True, nullable=False
    )  # Offline idempotency key
    incident_id = Column(
        String(36), ForeignKey("incidents.id"), nullable=True, index=True
    )
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    accuracy_m = Column(Float, default=5.0)
    disruption_type = Column(
        String(50), nullable=False
    )  # Landslide, River Breach, Mudflow, Culvert Collapse
    severity = Column(String(30), nullable=False, default="CRITICAL")
    description = Column(Text, nullable=False)
    media_files_json = Column(Text, nullable=True)  # Array of URLs/Media IDs
    offline_created_at = Column(DateTime, nullable=False, index=True)
    synced_at = Column(DateTime, default=lambda: datetime.now(UTC), index=True)
    sync_status = Column(
        String(30), default="SYNCED"
    )  # PENDING, SYNCED, CONFLICT_FLAGGED
    device_id = Column(String(100), nullable=True)

    incident = relationship("Incident", back_populates="field_reports")
    reporter = relationship("User", back_populates="field_reports")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_url = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False)  # image/jpeg, video/mp4, application/pdf
    size_bytes = Column(Integer, default=0)
    checksum_sha256 = Column(String(64), nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(UTC))
    virus_scanned = Column(Boolean, default=True)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)


class VerificationTask(Base):
    __tablename__ = "verification_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(
        String(36), ForeignKey("incidents.id"), nullable=False, index=True
    )
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        String(30), default="PENDING"
    )  # PENDING, IN_PROGRESS, VERIFIED, FALSE_ALARM
    deadline = Column(DateTime, nullable=False)
    priority = Column(String(20), default="URGENT")
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)

    incident = relationship("Incident", back_populates="verification_tasks")
