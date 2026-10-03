from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class RouteRequest(Base):
    __tablename__ = "route_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    origin_name = Column(String(100), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    destination_name = Column(String(100), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)
    vehicle_type = Column(String(50), default="MULTI_AXLE_HEAVY")
    cargo_type = Column(String(50), default="CRITICAL_RELIEF")
    departure_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    optimization_priority = Column(String(50), default="SAFEST") # SAFEST, FASTEST, LOW_DISRUPTION, HEAVY_CLEARANCE, EMERGENCY
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    route_options = relationship("RouteOption", back_populates="request")

class RouteOption(Base):
    __tablename__ = "route_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), ForeignKey("route_requests.id"), nullable=False, index=True)
    option_tag = Column(String(10), nullable=False) # A, B, C
    route_name = Column(String(150), nullable=False) # e.g. "NH-27 via Jatinga Bypass"
    corridor_summary = Column(String(250), nullable=True) # "Guwahati -> Nagaon -> Lumding -> Jatinga -> Haflong"
    waypoints_geojson = Column(Text, nullable=False) # GeoJSON LineString coordinates
    distance_km = Column(Float, nullable=False)
    estimated_travel_time_hours = Column(Float, nullable=False)
    expected_delay_hours = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.15) # Composite risk [0 to 1]
    slide_risk_pct = Column(Float, default=14.0)
    max_gradient_m = Column(Float, default=920.0)
    blocked_segments_count = Column(Integer, default=0)
    confidence = Column(Float, default=0.96)
    is_recommended = Column(Boolean, default=False)
    operational_status = Column(String(30), default="OPTIMAL") # OPTIMAL, RESTRICTED, HIGH_RISK, IMPASSABLE
    standby_excavators = Column(Integer, default=3)
    tolls_count = Column(Integer, default=5)

    request = relationship("RouteRequest", back_populates="route_options")

class RouteAssignment(Base):
    __tablename__ = "route_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), nullable=False, index=True)
    route_option_id = Column(String(36), ForeignKey("route_options.id"), nullable=False)
    dispatcher_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(30), default="ACTIVE") # ACTIVE, REOPTIMIZED, TERMINATED

class TravelTimePrediction(Base):
    __tablename__ = "travel_time_predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    predicted_travel_time_min = Column(Float, nullable=False)
    delay_minutes = Column(Float, default=0.0)
    model_version = Column(String(50), default="lgbm-eta-v2.1")
    confidence = Column(Float, default=0.92)
