from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    license_number = Column(String(50), unique=True, nullable=False)
    blood_group = Column(String(10), default="O+")
    emergency_contact = Column(String(20), nullable=True)
    status = Column(String(30), default="AVAILABLE") # AVAILABLE, ON_TRIP, RESTING, OFF_DUTY

    vehicles = relationship("Vehicle", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    registration_number = Column(String(30), unique=True, nullable=False, index=True) # e.g. AS-01-GB-4091
    type = Column(String(50), nullable=False) # CRYO_TANKER, MULTI_AXLE_HEAVY, 4X4_TACTICAL_PICKUP, AMBULANCE, NDRF_EVAC
    capacity_mt = Column(Float, default=15.0)
    owner = Column(String(100), default="Govt of Assam / NEC Relief Logistics")
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=True)
    current_status = Column(String(30), default="ACTIVE", index=True) # ACTIVE, IN_TRANSIT, BREAKDOWN, IDLE, SOS_EMERGENCY
    last_lat = Column(Float, nullable=True)
    last_lon = Column(Float, nullable=True)
    last_speed_kmh = Column(Float, default=0.0)
    last_heading_deg = Column(Float, default=0.0)
    last_altitude_m = Column(Float, default=300.0)
    cryo_temp_c = Column(Float, nullable=True) # Critical for cryogenic medicine/oxygen
    last_ping_time = Column(DateTime, nullable=True, index=True)

    driver = relationship("Driver", back_populates="vehicles")
    gps_readings = relationship("GPSReading", back_populates="vehicle", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="vehicle")

class GPSReading(Base):
    __tablename__ = "gps_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String(36), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=0.0)
    heading_deg = Column(Float, default=0.0)
    accuracy_m = Column(Float, default=2.5)
    altitude_m = Column(Float, default=250.0)
    ignition_status = Column(Boolean, default=True)
    engine_temp_c = Column(Float, default=85.0)
    cryo_temp_c = Column(Float, nullable=True)
    navic_satellite_count = Column(Integer, default=9)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    vehicle = relationship("Vehicle", back_populates="gps_readings")

class Consignment(Base):
    __tablename__ = "consignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consignment_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. CON-NER-2026-881
    type = Column(String(50), nullable=False) # MEDICAL_OXYGEN, CRYO_VACCINES, POL_FUEL, FOODGRAINS_FCI, DISASTER_RELIEF
    description = Column(String(200), nullable=False)
    quantity_mt = Column(Float, default=10.0)
    origin_name = Column(String(100), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    destination_name = Column(String(100), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)
    priority = Column(String(30), default="GRADE_1_CRITICAL") # GRADE_1_CRITICAL, HIGH, STANDARD
    temperature_requirement = Column(String(50), nullable=True) # e.g. "-20C to -10C"
    status = Column(String(30), default="QUEUED", index=True) # QUEUED, ASSIGNED, IN_TRANSIT, DELIVERED, ABORTED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    trips = relationship("Trip", back_populates="consignment")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. TRIP-GUW-SIL-704
    vehicle_id = Column(String(36), ForeignKey("vehicles.id"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.id"), nullable=False, index=True)
    consignment_id = Column(String(36), ForeignKey("consignments.id"), nullable=False, index=True)
    planned_route_id = Column(String(36), nullable=True)
    planned_route_geojson = Column(Text, nullable=True)
    actual_route_geojson = Column(Text, nullable=True)
    departure_time = Column(DateTime, nullable=True)
    estimated_arrival_time = Column(DateTime, nullable=True)
    actual_arrival_time = Column(DateTime, nullable=True)
    status = Column(String(30), default="IN_TRANSIT", index=True) # SCHEDULED, IN_TRANSIT, DELAYED, SOS_DISTRESS, COMPLETED
    current_delay_min = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    consignment = relationship("Consignment", back_populates="trips")
    delivery_proof = relationship("DeliveryProof", back_populates="trip", uselist=False)

class DeliveryProof(Base):
    __tablename__ = "delivery_proofs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = Column(String(36), ForeignKey("trips.id"), unique=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    photo_url = Column(String(500), nullable=True)
    receiver_name = Column(String(120), nullable=False)
    receiver_designation = Column(String(100), default="District Health Officer")
    digital_signature = Column(Text, nullable=True)
    verified = Column(Boolean, default=True)

    trip = relationship("Trip", back_populates="delivery_proof")

class Geofence(Base):
    __tablename__ = "geofences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    type = Column(String(50), default="CORRIDOR") # WAREHOUSE, BUFFER_ZONE, DISASTER_HOTSPOT, SENSITIVE_PASS
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    radius_meters = Column(Float, default=1000.0)
    polygon_geojson = Column(Text, nullable=True)
