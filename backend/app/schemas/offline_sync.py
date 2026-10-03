from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class SyncQueueItem(BaseModel):
    queue_id: str
    client_uuid: str
    operation: str # CREATE_FIELD_REPORT, UPDATE_ROAD_STATUS, BATCH_GPS, LOG_INCIDENT_VERIFICATION
    payload: Dict[str, Any]
    client_timestamp: datetime
    device_id: str
    retry_count: int = 0

class SyncBatchRequest(BaseModel):
    device_id: str
    sync_session_id: str
    queue_items: List[SyncQueueItem]

class SyncItemResult(BaseModel):
    client_uuid: str
    status: str # SUCCESS, CONFLICT_FLAGGED, REJECTED, DUPLICATE_SKIPPED
    server_id: Optional[str] = None
    conflict_details: Optional[str] = None
    processed_at: datetime

class SyncBatchResponse(BaseModel):
    sync_session_id: str
    processed_count: int
    success_count: int
    conflict_count: int
    results: List[SyncItemResult]

class DeltaSyncRequest(BaseModel):
    last_synced_at: Optional[datetime] = None
    district_filter: Optional[str] = None
    include_tiles: bool = False

class DeltaSyncResponse(BaseModel):
    server_timestamp: datetime
    updated_roads: List[Dict[str, Any]]
    updated_segments: List[Dict[str, Any]]
    active_incidents: List[Dict[str, Any]]
    active_alerts: List[Dict[str, Any]]
    active_convoys: List[Dict[str, Any]]
