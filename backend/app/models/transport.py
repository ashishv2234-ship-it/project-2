from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class State(Base):
    __tablename__ = "states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False, index=True) # AS, ML, AR, NL, MN, MZ, TR, SK
    capital = Column(String(100), nullable=False)
    boundary_geojson = Column(Text, nullable=True)

    districts = relationship("District", back_populates="state")

class District(Base):
    __tablename__ = "districts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id = Column(String(36), ForeignKey("states.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    code = Column(String(20), nullable=True)
    isolation_index = Column(Float, default=0.0) # 0.0 (fully connected) to 1.0 (critically isolated)
    connectivity_status = Column(String(30), default="CONNECTED") # CONNECTED, RESTRICTED, SEVERED, FLOOD_CUTOFF
    critical_facilities_count = Column(Integer, default=5)
    center_lat = Column(Float, nullable=True)
    center_lon = Column(Float, nullable=True)
    boundary_geojson = Column(Text, nullable=True)

    state = relationship("State", back_populates="districts")
    infrastructure = relationship("InfrastructureNode", back_populates="district")

class AdministrativeBoundary(Base):
    __tablename__ = "administrative_boundaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(50), nullable=False) # STATE, DISTRICT, BLOCK
    entity_id = Column(String(36), nullable=False, index=True)
    boundary_geojson = Column(Text, nullable=False)

class Road(Base):
    __tablename__ = "roads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True) # NH-27, NH-6, NH-102, SH-4, BRO-BorderRoad
    type = Column(String(50), nullable=False) # NATIONAL_HIGHWAY, STATE_HIGHWAY, BRO_TACTICAL, PMGSY_RURAL
    surface = Column(String(50), default="ASPHALT") # ASPHALT, CONCRETE, GRAVEL, UNMETALLED
    lanes = Column(Integer, default=2)
    owner_department = Column(String(100), default="NHAI") # NHAI, BRO, STATE_PWD, PMGSY
    status = Column(String(30), default="OPEN", index=True) # OPEN, RESTRICTED, HIGH_RISK, BLOCKED, UNVERIFIED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    segments = relationship("RoadSegment", back_populates="road")
    bridges = relationship("Bridge", back_populates="road")

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    road_id = Column(String(36), ForeignKey("roads.id"), nullable=False, index=True)
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    start_point_name = Column(String(100), nullable=False)
    end_point_name = Column(String(100), nullable=False)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    length_km = Column(Float, nullable=False)
    elevation_m = Column(Float, default=300.0)
    slope_degrees = Column(Float, default=5.0)
    flood_risk_score = Column(Float, default=0.1) # 0.0 to 1.0
    landslide_risk_score = Column(Float, default=0.1) # 0.0 to 1.0
    current_status = Column(String(30), default="OPEN", index=True) # OPEN, RESTRICTED, HIGH_RISK, BLOCKED, UNVERIFIED
    speed_limit_kmh = Column(Float, default=60.0)
    current_travel_time_min = Column(Float, default=15.0)
    expected_delay_min = Column(Float, default=0.0)
    geometry_geojson = Column(Text, nullable=True) # Array of coordinates
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    road = relationship("Road", back_populates="segments")
    status_events = relationship("RoadStatusEvent", back_populates="segment")

class Bridge(Base):
    __tablename__ = "bridges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)
    road_id = Column(String(36), ForeignKey("roads.id"), nullable=False, index=True)
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    load_capacity_mt = Column(Float, default=40.0) # Metric tons
    status = Column(String(30), default="OPERATIONAL") # OPERATIONAL, WEIGHT_RESTRICTED, SUBMERGED, STRUCTURALLY_DAMAGED, CLOSED
    last_inspection_date = Column(DateTime, nullable=True)
    structural_health_index = Column(Float, default=95.0) # 0 to 100%

    road = relationship("Road", back_populates="bridges")

class InfrastructureNode(Base):
    __tablename__ = "infrastructure_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)
    type = Column(String(50), nullable=False, index=True) # CHECKPOINT, FERRY_ROUTE, WAREHOUSE, HOSPITAL, RELIEF_CAMP, HELIPAD
    district_id = Column(String(36), ForeignKey("districts.id"), nullable=True, index=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    capacity_desc = Column(String(100), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    is_operational = Column(Boolean, default=True)

    district = relationship("District", back_populates="infrastructure")

class RoadStatusEvent(Base):
    __tablename__ = "road_status_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = Column(String(36), ForeignKey("road_segments.id"), nullable=False, index=True)
    status = Column(String(30), nullable=False, index=True) # OPEN, RESTRICTED, HIGH_RISK, BLOCKED, UNVERIFIED
    source = Column(String(50), nullable=False) # FIELD_REPORT, SATELLITE_RADAR, BRO_TELEMETRY, POLICE_CONTROL, CITIZEN
    confidence = Column(Float, default=0.95)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    end_time = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    verified_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    segment = relationship("RoadSegment", back_populates="status_events")
