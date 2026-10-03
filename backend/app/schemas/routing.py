from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class RoutePlanRequest(BaseModel):
    origin_name: str
    origin_lat: float
    origin_lon: float
    destination_name: str
    dest_lat: float
    dest_lon: float
    vehicle_type: Optional[str] = "MULTI_AXLE_HEAVY"
    cargo_type: Optional[str] = "CRITICAL_RELIEF"
    departure_time: Optional[datetime] = None
    optimization_priority: Optional[str] = "SAFEST" # SAFEST, FASTEST, LOW_DISRUPTION, HEAVY_CLEARANCE, EMERGENCY
    alpha_travel_time: Optional[float] = 0.45
    beta_risk: Optional[float] = 0.40
    gamma_cost: Optional[float] = 0.15

class RouteOptionResponse(BaseModel):
    id: str
    option_tag: str # A, B, C
    route_name: str
    corridor_summary: Optional[str] = None
    waypoints: List[List[float]] # [[lat, lon], ...]
    distance_km: float
    estimated_travel_time_hours: float
    expected_delay_hours: float
    risk_score: float
    slide_risk_pct: float
    max_gradient_m: float
    blocked_segments_count: int
    confidence: float
    is_recommended: bool
    operational_status: str # OPTIMAL, RESTRICTED, HIGH_RISK, IMPASSABLE
    standby_excavators: int
    tolls_count: int

class RoutePlanResult(BaseModel):
    request_id: str
    origin: str
    destination: str
    priority: str
    generated_at: datetime
    is_direct_route_available: bool
    alternative_safe_shelter: Optional[str] = None
    routes: List[RouteOptionResponse]

class RouteAssignRequest(BaseModel):
    trip_id: str
    route_option_id: str

class RouteReoptimizeRequest(BaseModel):
    trip_id: str
    current_lat: float
    current_lon: float
    detected_blockade_segment_id: Optional[str] = None

class EmergencyCorridorResponse(BaseModel):
    corridor_code: str
    name: str
    status: str
    from_city: str
    to_city: str
    clearance_priority: str
    escort_regiment: str
    current_convoy_count: int
    elevation_profile: List[Dict[str, Any]]

class DriverTurnStep(BaseModel):
    step_number: int
    instruction: str
    highway: str
    distance_km: float
    surface_type: str # ASPHALT, CONCRETE, GRAVEL
    speed_kmh: int
    telecom_coverage: str # 4G_5G, 2G_VOICE, NAVIC_SATELLITE_ONLY
    fuel_stops: Optional[str] = None
    hazard_status: str # ALL_CLEAR, CAUTION_RAIN, CONTROLLED_ESCORT

class DriverSafetyChecklist(BaseModel):
    blockades_on_path: int
    bridge_load_safe: bool
    bridge_max_capacity_mt: float
    weather_clearance: str
    landslide_risk_level: str
    convoy_escort_required: bool
    convoy_schedule: Optional[str] = None
    police_checkpoints: List[str]
    emergency_helpline_ner: str
    emergency_helpline_bro: str
    crane_recovery_contact: str

class DriverRoutePlanRequest(BaseModel):
    origin_name: str
    destination_name: str
    vehicle_type: Optional[str] = "HEAVY_TRUCK_3AXLE" # HEAVY_TRUCK_3AXLE, CRYO_TANKER, AMBULANCE_4X4, LIGHT_CARGO
    gross_weight_mt: Optional[float] = 18.5
    cargo_priority: Optional[str] = "MEDICAL_OXYGEN_SALINE"
    avoid_night_transit: Optional[bool] = False

class DriverSafeRouteResponse(BaseModel):
    route_id: str
    route_name: str
    origin_name: str
    destination_name: str
    vehicle_type: str
    gross_weight_mt: float
    zero_blockade_verified: bool
    distance_km: float
    estimated_travel_time_hours: float
    expected_delay_minutes: float
    safety_rating: str # 100% HAZARD-FREE, ALL-CLEAR, MONITORED_ESCORT
    waypoints: List[List[float]]
    turn_by_turn: List[DriverTurnStep]
    safety_checklist: DriverSafetyChecklist
    offline_pass_token: str
