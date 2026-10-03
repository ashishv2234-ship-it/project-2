from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    type: str
    severity: str = "HIGH"
    district_id: str | None = None
    road_id: str | None = None
    location_desc: str
    message: str
    expires_at: datetime | None = None


class AlertResponse(BaseModel):
    id: str
    type: str
    severity: str
    district_id: str | None = None
    road_id: str | None = None
    location_desc: str
    message: str
    status: str
    created_at: datetime
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


class AlertNotifyRequest(BaseModel):
    channels: list[str] | None = ["WEBSOCKET", "PUSH", "SMS"]
    target_districts: list[str] | None = None
    priority: str = "HIGH"


class NotificationResponse(BaseModel):
    id: str
    alert_id: str | None = None
    channel: str
    language: str
    message_text: str
    status: str
    sent_at: datetime
    read_at: datetime | None = None

    class Config:
        from_attributes = True


class NotificationPreferencesRequest(BaseModel):
    channels: list[str]
    districts: list[str]
    alert_types: list[str]
    language: str


class EmergencyEventCreate(BaseModel):
    event_code: str
    title: str
    type: str = "MONSOON_SURGE"
    level: str = "LEVEL_3"
    affected_districts: list[str]
    priority_corridors: list[str]


class EmergencyEventUpdate(BaseModel):
    title: str | None = None
    level: str | None = None
    affected_districts: list[str] | None = None
    priority_corridors: list[str] | None = None
    is_active: bool | None = None


class EmergencyEventResponse(BaseModel):
    id: str
    event_code: str
    title: str
    type: str
    level: str
    affected_districts: list[str]
    priority_corridors: list[str]
    activated_by: str
    start_time: datetime
    end_time: datetime | None = None
    is_active: bool
