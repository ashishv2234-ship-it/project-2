from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class AlertCreate(BaseModel):
    type: str
    severity: str = "HIGH"
    district_id: Optional[str] = None
    road_id: Optional[str] = None
    location_desc: str
    message: str
    expires_at: Optional[datetime] = None

class AlertResponse(BaseModel):
    id: str
    type: str
    severity: str
    district_id: Optional[str] = None
    road_id: Optional[str] = None
    location_desc: str
    message: str
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlertNotifyRequest(BaseModel):
    channels: Optional[List[str]] = ["WEBSOCKET", "PUSH", "SMS"]
    target_districts: Optional[List[str]] = None
    priority: str = "HIGH"

class NotificationResponse(BaseModel):
    id: str
    alert_id: Optional[str] = None
    channel: str
    language: str
    message_text: str
    status: str
    sent_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationPreferencesRequest(BaseModel):
    channels: List[str]
    districts: List[str]
    alert_types: List[str]
    language: str

class EmergencyEventCreate(BaseModel):
    event_code: str
    title: str
    type: str = "MONSOON_SURGE"
    level: str = "LEVEL_3"
    affected_districts: List[str]
    priority_corridors: List[str]

class EmergencyEventUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
    affected_districts: Optional[List[str]] = None
    priority_corridors: Optional[List[str]] = None
    is_active: Optional[bool] = None

class EmergencyEventResponse(BaseModel):
    id: str
    event_code: str
    title: str
    type: str
    level: str
    affected_districts: List[str]
    priority_corridors: List[str]
    activated_by: str
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool
