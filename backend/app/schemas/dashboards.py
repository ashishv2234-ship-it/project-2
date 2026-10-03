from typing import Any

from pydantic import BaseModel


class StateOverviewResponse(BaseModel):
    state_code: str
    state_name: str
    total_roads_km: float
    operational_pct: float
    active_blockades: int
    cutoff_districts: int
    convoys_en_route: int
    telemetry_stations_active: int
    telemetry_stations_total: int
    navic_sync_pct: float
    monsoon_surge_level: str
    active_incidents: list[dict[str, Any]]
    chokepoints: list[dict[str, Any]]


class DistrictDetailResponse(BaseModel):
    district_id: str
    district_name: str
    state_name: str
    isolation_index: float
    connectivity_status: str
    critical_facilities: dict[str, int]
    active_incidents_count: int
    weather_alert_level: str
    rainfall_past_24h_mm: float
    accessible_highways: list[str]
    blocked_highways: list[str]


class LogisticsBottleneckItem(BaseModel):
    corridor_code: str
    corridor_name: str
    chokepoint_name: str
    lat: float
    lon: float
    issue_type: str  # LANDSLIDE, BRIDGE_LOAD, FLOODING, ROAD_WORK
    severity: str
    traffic_delay_min: float
    pwd_excavators_on_standby: int
    bypass_available: bool


class EmergencyOverviewResponse(BaseModel):
    active_emergency_event: dict[str, Any] | None = None
    sos_beacons_active: int
    priority_corridors_status: list[dict[str, Any]]
    relief_camps_supplied_pct: float
    cryo_cargo_status_summary: dict[str, Any]


class VehicleMovementResponse(BaseModel):
    total_vehicles_active: int
    vehicles_in_transit: int
    vehicles_stalled_or_delayed: int
    cryo_alerts_count: int
    live_fleet: list[dict[str, Any]]


class AnalyticsDeliveryPerformance(BaseModel):
    on_time_delivery_rate: float
    average_delay_minutes: float
    consignments_delivered_this_week: int
    critical_medical_sla_compliance: float
    convoys_rerouted_due_to_ai: int


class AnalyticsDisruptionTrends(BaseModel):
    time_series: list[
        dict[str, Any]
    ]  # e.g. [{ "date": "2026-09-27", "landslides": 4, "floods": 2 }]
    highest_risk_corridors: list[dict[str, Any]]
