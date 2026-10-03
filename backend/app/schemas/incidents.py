from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class IncidentCreate(BaseModel):
    type: str # landslide, flood, road_damage, bridge_closure, accident, congestion, vehicle_breakdown
    severity: str = "HIGH" # LOW, MODERATE, HIGH, CRITICAL
    location_desc: str
    lat: float
    lon: float
    road_segment_id: Optional[str] = None
    district_id: Optional[str] = None
    description: str
    estimated_clearance_hours: float = 4.0

class IncidentUpdate(BaseModel):
    severity: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    estimated_clearance_hours: Optional[float] = None

class IncidentVerifyRequest(BaseModel):
    verified: bool
    remarks: Optional[str] = None
    updated_severity: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    type: str
    severity: str
    location_desc: str
    lat: float
    lon: float
    road_segment_id: Optional[str] = None
    district_id: Optional[str] = None
    description: str
    status: str
    reported_by: Optional[str] = None
    verified_by: Optional[str] = None
    estimated_clearance_hours: float
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FieldReportCreate(BaseModel):
    client_uuid: str # Offline client generated UUID
    incident_id: Optional[str] = None
    lat: float
    lon: float
    accuracy_m: float = 5.0
    disruption_type: str
    severity: str = "CRITICAL"
    description: str
    media_files: Optional[List[str]] = None
    offline_created_at: datetime
    device_id: Optional[str] = None

class FieldReportResponse(BaseModel):
    id: str
    client_uuid: str
    incident_id: Optional[str] = None
    reporter_id: str
    lat: float
    lon: float
    accuracy_m: float
    disruption_type: str
    severity: str
    description: str
    media_files: Optional[List[str]] = None
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
