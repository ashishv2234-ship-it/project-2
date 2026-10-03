from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WeatherCurrentResponse(BaseModel):
    station_name: str
    lat: float
    lon: float
    timestamp: datetime
    rainfall_mm: float
    temperature_c: float
    wind_kmh: float
    humidity_pct: float
    warning_level: str
    source: str


class WeatherForecastResponse(BaseModel):
    lat: float
    lon: float
    forecast_time: datetime
    rainfall_predicted_mm: float
    warning_level: str
    bulletin_text: str | None = None
    source: str


class WarningResponse(BaseModel):
    district_id: str | None = None
    district_name: str
    warning_level: str  # GREEN, YELLOW, ORANGE, RED
    bulletin: str
    effective_until: datetime
    issued_at: datetime


class SegmentRiskResponse(BaseModel):
    segment_id: str
    road_name: str
    risk_type: str
    probability: float
    severity: str
    valid_from: datetime
    valid_to: datetime
    model_version: str
    confidence: float
    contributing_factors: dict[str, Any] | None = None


class DistrictRiskSummaryResponse(BaseModel):
    district_id: str
    district_name: str
    average_landslide_risk: float
    average_flood_risk: float
    critical_segments_count: int
    highest_risk_road: str
    imd_warning_level: str


class RiskRecomputeRequest(BaseModel):
    district_id: str | None = None
    force_all: bool = False
