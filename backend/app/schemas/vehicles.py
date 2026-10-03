from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class VehicleCreate(BaseModel):
    registration_number: str
    type: str # CRYO_TANKER, MULTI_AXLE_HEAVY, 4X4_TACTICAL_PICKUP, AMBULANCE, NDRF_EVAC
    capacity_mt: float = 15.0
    owner: str = "Govt of Assam Logistics"
    driver_id: Optional[str] = None

class VehicleResponse(BaseModel):
    id: str
    registration_number: str
    type: str
    capacity_mt: float
    owner: str
    driver_id: Optional[str] = None
    current_status: str
    last_lat: Optional[float] = None
    last_lon: Optional[float] = None
    last_speed_kmh: Optional[float] = 0.0
    last_heading_deg: Optional[float] = 0.0
    cryo_temp_c: Optional[float] = None
    last_ping_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class GPSReadingCreate(BaseModel):
    timestamp: datetime
    latitude: float
    longitude: float
    speed_kmh: float = 0.0
    heading_deg: float = 0.0
    accuracy_m: float = 2.5
    altitude_m: float = 250.0
    ignition_status: bool = True
    engine_temp_c: float = 85.0
    cryo_temp_c: Optional[float] = None
    navic_satellite_count: int = 9

class GPSBatchIngestRequest(BaseModel):
    vehicle_id: str
    readings: List[GPSReadingCreate]

class ConsignmentCreate(BaseModel):
    consignment_number: str
    type: str
    description: str
    quantity_mt: float
    origin_name: str
    origin_lat: float
    origin_lon: float
    destination_name: str
    dest_lat: float
    dest_lon: float
    priority: str = "GRADE_1_CRITICAL"
    temperature_requirement: Optional[str] = None

class ConsignmentResponse(ConsignmentCreate):
    id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TripCreate(BaseModel):
    vehicle_id: str
    driver_id: str
    consignment_id: str
    planned_route_id: Optional[str] = None
    departure_time: Optional[datetime] = None

class TripResponse(BaseModel):
    id: str
    trip_code: str
    vehicle_id: str
    driver_id: str
    consignment_id: str
    departure_time: Optional[datetime] = None
    estimated_arrival_time: Optional[datetime] = None
    status: str
    current_delay_min: float
    created_at: datetime

    class Config:
        from_attributes = True

class DeliveryProofCreate(BaseModel):
    lat: float
    lon: float
    photo_url: Optional[str] = None
    receiver_name: str
    receiver_designation: str = "Camp In-Charge"
    digital_signature: Optional[str] = None

class GeofenceCreate(BaseModel):
    name: str
    type: str
    center_lat: float
    center_lon: float
    radius_meters: float = 1000.0
    polygon_geojson: Optional[str] = None
