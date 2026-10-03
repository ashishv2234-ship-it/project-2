from datetime import datetime

from pydantic import BaseModel


class RoadBase(BaseModel):
    name: str
    code: str
    type: str
    surface: str
    lanes: int
    owner_department: str
    status: str


class RoadResponse(RoadBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class RoadSegmentBase(BaseModel):
    road_id: str
    start_point_name: str
    end_point_name: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    length_km: float
    elevation_m: float
    slope_degrees: float
    flood_risk_score: float
    landslide_risk_score: float
    current_status: str
    speed_limit_kmh: float
    current_travel_time_min: float
    expected_delay_min: float
    geometry_geojson: str | None = None


class RoadSegmentResponse(RoadSegmentBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True


class BridgeResponse(BaseModel):
    id: str
    name: str
    road_id: str
    lat: float
    lon: float
    load_capacity_mt: float
    status: str
    structural_health_index: float
    last_inspection_date: datetime | None = None

    class Config:
        from_attributes = True


class RoadStatusEventCreate(BaseModel):
    segment_id: str
    status: str  # OPEN, RESTRICTED, HIGH_RISK, BLOCKED, UNVERIFIED
    source: str
    confidence: float = 0.95
    reason: str | None = None


class DistrictConnectivityResponse(BaseModel):
    district_id: str
    district_name: str
    isolation_index: float
    connectivity_status: str
    critical_facilities_count: int
    open_routes_count: int
    blocked_routes_count: int
    nearest_accessible_depot: str


class DistrictInfoResponse(BaseModel):
    id: str
    name: str
    state_code: str
    state_name: str
    isolation_index: float
    connectivity_status: str  # CONNECTED, RESTRICTED, SEVERED, FLOOD_CUTOFF
    critical_facilities_count: int
    hospitals_count: int
    relief_camps_count: int
    center_lat: float | None = None
    center_lon: float | None = None
    problem_type: str | None = None
    problem_summary: str
    problem_description: str
    chokepoint_location: str
    chokepoint_lat: float | None = None
    chokepoint_lon: float | None = None
    operational_impact: str
    restoration_eta: str
    recommended_contingency: str


class AccessibilitySummaryResponse(BaseModel):
    total_network_km: float
    operational_pct: float
    active_blockades_count: int
    cutoff_districts_count: int
    convoys_in_transit_count: int
    last_updated: datetime
