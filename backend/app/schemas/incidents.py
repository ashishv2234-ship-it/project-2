from datetime import datetime

from pydantic import BaseModel


class IncidentCreate(BaseModel):
    type: str  # landslide, flood, road_damage, bridge_closure, accident, congestion, vehicle_breakdown
    severity: str = "HIGH"  # LOW, MODERATE, HIGH, CRITICAL
    location_desc: str
    lat: float
    lon: float
    road_segment_id: str | None = None
    district_id: str | None = None
    description: str
    estimated_clearance_hours: float = 4.0


class IncidentUpdate(BaseModel):
    severity: str | None = None
    description: str | None = None
    status: str | None = None
    estimated_clearance_hours: float | None = None


class IncidentVerifyRequest(BaseModel):
    verified: bool
    remarks: str | None = None
    updated_severity: str | None = None


class IncidentResponse(BaseModel):
    id: str
    type: str
    severity: str
    location_desc: str
    lat: float
    lon: float
    road_segment_id: str | None = None
    district_id: str | None = None
    description: str
    status: str
    reported_by: str | None = None
    verified_by: str | None = None
    estimated_clearance_hours: float
    created_at: datetime
    resolved_at: datetime | None = None

    class Config:
        from_attributes = True


class FieldReportCreate(BaseModel):
    client_uuid: str  # Offline client generated UUID
    incident_id: str | None = None
    lat: float
    lon: float
    accuracy_m: float = 5.0
    disruption_type: str
    severity: str = "CRITICAL"
    description: str
    media_files: list[str] | None = None
    offline_created_at: datetime
    device_id: str | None = None


class FieldReportResponse(BaseModel):
    id: str
    client_uuid: str
    incident_id: str | None = None
    reporter_id: str
    lat: float
    lon: float
    accuracy_m: float
    disruption_type: str
    severity: str
    description: str
    media_files: list[str] | None = None
    offline_created_at: datetime
    synced_at: datetime
    sync_status: str

    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    media_id: str
    file_url: str
    checksum_sha256: str
    size_bytes: int
    virus_scanned: bool
