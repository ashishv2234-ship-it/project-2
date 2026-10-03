from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer
from app.core.database import Base

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    station_name = Column(String(100), nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    rainfall_mm = Column(Float, default=0.0) # Past 1h / 24h rainfall
    temperature_c = Column(Float, default=24.0)
    wind_kmh = Column(Float, default=12.0)
    humidity_pct = Column(Float, default=85.0)
    source = Column(String(50), default="IMD_AWS") # IMD_AWS, IMD_DOPPLER_RADAR, CWC_HYDROMET

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    forecast_time = Column(DateTime, nullable=False, index=True)
    rainfall_predicted_mm = Column(Float, default=0.0)
    warning_level = Column(String(20), default="GREEN") # GREEN, YELLOW, ORANGE, RED
    bulletin_text = Column(Text, nullable=True)
    source = Column(String(50), default="IMD_REGIONAL_METEOROLOGY")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class FloodRiskZone(Base):
    __tablename__ = "flood_risk_zones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    river_basin = Column(String(100), default="Brahmaputra")
    current_water_level_m = Column(Float, default=105.2)
    danger_level_m = Column(Float, default=105.0)
    risk_level = Column(String(20), default="HIGH") # LOW, MODERATE, HIGH, SEVERE
    polygon_geojson = Column(Text, nullable=True)

class LandslideRiskZone(Base):
    __tablename__ = "landslide_risk_zones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    slope_angle_degrees = Column(Float, default=42.0)
    soil_type = Column(String(50), default="LOOSE_SHALE_AND_SILT")
    susceptibility_index = Column(Float, default=0.78) # 0 to 1.0
    risk_level = Column(String(20), default="HIGH") # LOW, MODERATE, HIGH, CRITICAL
    polygon_geojson = Column(Text, nullable=True)

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    risk_type = Column(String(50), nullable=False, index=True) # LANDSLIDE, FLASH_FLOOD, BRIDGE_COLLAPSE, ROAD_DAMAGE, CONGESTION
    probability = Column(Float, nullable=False) # 0.0 to 1.0
    severity = Column(String(20), nullable=False) # LOW, MODERATE, HIGH, CRITICAL
    valid_from = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    valid_to = Column(DateTime, nullable=False, index=True)
    model_version = Column(String(50), default="xgboost-ner-hazard-v2.4")
    confidence = Column(Float, default=0.91)
    contributing_factors_json = Column(Text, nullable=True) # e.g. {"rainfall_weight": 0.45, "slope_weight": 0.35}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
