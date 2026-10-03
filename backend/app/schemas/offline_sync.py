from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SyncQueueItem(BaseModel):
    queue_id: str
    client_uuid: str
    operation: str  # CREATE_FIELD_REPORT, UPDATE_ROAD_STATUS, BATCH_GPS, LOG_INCIDENT_VERIFICATION
    payload: dict[str, Any]
    client_timestamp: datetime
    device_id: str
    retry_count: int = 0


class SyncBatchRequest(BaseModel):
    device_id: str
    sync_session_id: str
    queue_items: list[SyncQueueItem]


class SyncItemResult(BaseModel):
    client_uuid: str
    status: str  # SUCCESS, CONFLICT_FLAGGED, REJECTED, DUPLICATE_SKIPPED
    server_id: str | None = None
    conflict_details: str | None = None
    processed_at: datetime


class SyncBatchResponse(BaseModel):
    sync_session_id: str
    processed_count: int
    success_count: int
    conflict_count: int
    results: list[SyncItemResult]


class DeltaSyncRequest(BaseModel):
    last_synced_at: datetime | None = None
    district_filter: str | None = None
    include_tiles: bool = False


class DeltaSyncResponse(BaseModel):
    server_timestamp: datetime
    updated_roads: list[dict[str, Any]]
    updated_segments: list[dict[str, Any]]
    active_incidents: list[dict[str, Any]]
    active_alerts: list[dict[str, Any]]
    active_convoys: list[dict[str, Any]]
