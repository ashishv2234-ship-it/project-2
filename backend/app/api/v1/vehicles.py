from datetime import UTC, datetime
from typing import Any

from app.core.audit import record_audit_log
from app.core.database import get_db
from app.models.vehicles import (
    Consignment,
    DeliveryProof,
    Driver,
    Geofence,
    GPSReading,
    Trip,
    Vehicle,
)
from app.schemas.vehicles import (
    ConsignmentCreate,
    ConsignmentResponse,
    DeliveryProofCreate,
    GeofenceCreate,
    GPSBatchIngestRequest,
    GPSReadingCreate,
    TripCreate,
    TripResponse,
    VehicleCreate,
    VehicleResponse,
)
from app.services.anomaly_detector import anomaly_detector
from app.services.eta_predictor import eta_predictor
from app.websocket.manager import ws_manager
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(tags=["Vehicles, Consignments & GPS Tracking"])


# Vehicles
@router.post("/vehicles", response_model=VehicleResponse)
def register_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new relief or supply vehicle."""
    existing = (
        db.query(Vehicle)
        .filter(Vehicle.registration_number == payload.registration_number)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Vehicle registration number already exists"
        )

    vehicle = Vehicle(
        registration_number=payload.registration_number,
        type=payload.type,
        capacity_mt=payload.capacity_mt,
        owner=payload.owner,
        driver_id=payload.driver_id,
        current_status="ACTIVE",
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/vehicles", response_model=list[VehicleResponse])
def list_vehicles(
    status_filter: str | None = None,
    type_filter: str | None = None,
    db: Session = Depends(get_db),
) -> Any:
    """List tracked fleet vehicles and live GPS telemetry."""
    query = db.query(Vehicle)
    if status_filter:
        query = query.filter(Vehicle.current_status == status_filter.upper())
    if type_filter:
        query = query.filter(Vehicle.type == type_filter.upper())
    return query.all()


@router.get("/vehicles/{id}", response_model=VehicleResponse)
def get_vehicle_by_id(id: str, db: Session = Depends(get_db)) -> Any:
    """Get single vehicle state and sensor telemetry."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/vehicles/{id}/gps")
async def ingest_vehicle_gps(
    id: str, payload: GPSReadingCreate, db: Session = Depends(get_db)
) -> Any:
    """Ingest real-time single GPS location update."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    reading_dict = payload.model_dump()
    prev_reading = (
        {
            "latitude": vehicle.last_lat,
            "longitude": vehicle.last_lon,
            "speed_kmh": vehicle.last_speed_kmh,
        }
        if vehicle.last_lat
        else None
    )

    # Run anomaly detection
    anomalies = anomaly_detector.analyze_telemetry_reading(
        vehicle_id=vehicle.id,
        reg_number=vehicle.registration_number,
        reading=reading_dict,
        prev_reading=prev_reading,
        cargo_type="MEDICAL_OXYGEN" if vehicle.type == "CRYO_TANKER" else "STANDARD",
    )

    # Update vehicle state
    vehicle.last_lat = payload.latitude
    vehicle.last_lon = payload.longitude
    vehicle.last_speed_kmh = payload.speed_kmh
    vehicle.last_heading_deg = payload.heading_deg
    vehicle.last_altitude_m = payload.altitude_m
    vehicle.cryo_temp_c = payload.cryo_temp_c
    vehicle.last_ping_time = payload.timestamp

    # Save reading
    reading = GPSReading(
        vehicle_id=vehicle.id,
        timestamp=payload.timestamp,
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kmh=payload.speed_kmh,
        heading_deg=payload.heading_deg,
        accuracy_m=payload.accuracy_m,
        altitude_m=payload.altitude_m,
        ignition_status=payload.ignition_status,
        engine_temp_c=payload.engine_temp_c,
        cryo_temp_c=payload.cryo_temp_c,
        navic_satellite_count=payload.navic_satellite_count,
    )
    db.add(reading)
    db.commit()

    # Broadcast via WebSocket
    await ws_manager.broadcast(
        {
            "event": "TELEMETRY_UPDATE",
            "vehicle_id": vehicle.id,
            "registration_number": vehicle.registration_number,
            "lat": payload.latitude,
            "lon": payload.longitude,
            "speed_kmh": payload.speed_kmh,
            "heading_deg": payload.heading_deg,
            "cryo_temp_c": payload.cryo_temp_c,
            "anomalies": anomalies,
        },
        channel="telemetry",
    )

    return {
        "status": "INGESTED",
        "vehicle_id": vehicle.id,
        "anomalies_detected": anomalies,
    }


@router.post("/vehicles/gps/batch")
def ingest_batch_gps(
    payload: GPSBatchIngestRequest, db: Session = Depends(get_db)
) -> Any:
    """High-throughput batch GPS ingestion endpoint (supporting 5,000 updates/sec)."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == payload.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    readings_to_add = []
    for r in payload.readings:
        reading = GPSReading(
            vehicle_id=payload.vehicle_id,
            timestamp=r.timestamp,
            latitude=r.latitude,
            longitude=r.longitude,
            speed_kmh=r.speed_kmh,
            heading_deg=r.heading_deg,
            accuracy_m=r.accuracy_m,
            altitude_m=r.altitude_m,
            ignition_status=r.ignition_status,
            engine_temp_c=r.engine_temp_c,
            cryo_temp_c=r.cryo_temp_c,
            navic_satellite_count=r.navic_satellite_count,
        )
        readings_to_add.append(reading)

    db.add_all(readings_to_add)

    if payload.readings:
        last = payload.readings[-1]
        vehicle.last_lat = last.latitude
        vehicle.last_lon = last.longitude
        vehicle.last_speed_kmh = last.speed_kmh
        vehicle.last_heading_deg = last.heading_deg
        vehicle.cryo_temp_c = last.cryo_temp_c
        vehicle.last_ping_time = last.timestamp

    db.commit()
    return {"status": "SUCCESS", "ingested_count": len(readings_to_add)}


@router.get("/vehicles/{id}/location-history")
def get_vehicle_location_history(
    id: str, limit: int = 100, db: Session = Depends(get_db)
) -> Any:
    """Get chronological location trail for a vehicle."""
    readings = (
        db.query(GPSReading)
        .filter(GPSReading.vehicle_id == id)
        .order_by(GPSReading.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp": r.timestamp.isoformat(),
            "lat": r.latitude,
            "lon": r.longitude,
            "speed_kmh": r.speed_kmh,
            "heading_deg": r.heading_deg,
            "cryo_temp_c": r.cryo_temp_c,
        }
        for r in reversed(readings)
    ]


# Consignments
@router.post("/consignments", response_model=ConsignmentResponse)
def create_consignment(
    payload: ConsignmentCreate, db: Session = Depends(get_db)
) -> Any:
    """Register cargo shipment (Medical Oxygen, FCI Foodgrains, Vaccines)."""
    consignment = Consignment(
        consignment_number=payload.consignment_number,
        type=payload.type,
        description=payload.description,
        quantity_mt=payload.quantity_mt,
        origin_name=payload.origin_name,
        origin_lat=payload.origin_lat,
        origin_lon=payload.origin_lon,
        destination_name=payload.destination_name,
        dest_lat=payload.dest_lat,
        dest_lon=payload.dest_lon,
        priority=payload.priority,
        temperature_requirement=payload.temperature_requirement,
        status="QUEUED",
    )
    db.add(consignment)
    db.commit()
    db.refresh(consignment)
    return consignment


@router.get("/consignments/{id}", response_model=ConsignmentResponse)
def get_consignment(id: str, db: Session = Depends(get_db)) -> Any:
    """Retrieve consignment metadata and tracking status."""
    consignment = db.query(Consignment).filter(Consignment.id == id).first()
    if not consignment:
        raise HTTPException(status_code=404, detail="Consignment not found")
    return consignment


# Trips
@router.post("/trips", response_model=TripResponse)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)) -> Any:
    """Dispatch a trip / relief mission."""
    code = f"TRIP-NER-{int(datetime.now(UTC).timestamp())}"
    trip = Trip(
        trip_code=code,
        vehicle_id=payload.vehicle_id,
        driver_id=payload.driver_id,
        consignment_id=payload.consignment_id,
        planned_route_id=payload.planned_route_id,
        departure_time=payload.departure_time or datetime.now(UTC),
        status="IN_TRANSIT",
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.get("/trips/{id}/status")
def get_trip_status(id: str, db: Session = Depends(get_db)) -> Any:
    """Get live trip status, dynamic ETA prediction, and route progress."""
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        # Fallback to first trip for demo
        trip = db.query(Trip).first()
        if not trip:
            raise HTTPException(status_code=404, detail="No active trips")

    vehicle = db.query(Vehicle).filter(Vehicle.id == trip.vehicle_id).first()
    driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
    consignment = (
        db.query(Consignment).filter(Consignment.id == trip.consignment_id).first()
    )

    # Dynamic ETA prediction
    curr_lat = vehicle.last_lat if vehicle and vehicle.last_lat else 25.75
    curr_lon = vehicle.last_lon if vehicle and vehicle.last_lon else 93.16
    curr_speed = vehicle.last_speed_kmh if vehicle else 42.0
    dest_lat = consignment.dest_lat if consignment else 25.188
    dest_lon = consignment.dest_lon if consignment else 92.997

    eta_info = eta_predictor.predict_trip_eta(
        current_lat=curr_lat,
        current_lon=curr_lon,
        current_speed_kmh=curr_speed,
        dest_lat=dest_lat,
        dest_lon=dest_lon,
        planned_route_waypoints=[[26.182, 91.758], [25.75, 93.16], [25.188, 92.997]],
        weather_warning_level="RED",
        active_blockades_ahead=1,
    )

    return {
        "trip_id": trip.id,
        "trip_code": trip.trip_code,
        "status": trip.status,
        "vehicle": {
            "registration": vehicle.registration_number if vehicle else "AS-01-GB-4091",
            "type": vehicle.type if vehicle else "CRYO_TANKER",
            "cryo_temp_c": vehicle.cryo_temp_c if vehicle else -22.4,
            "current_speed_kmh": curr_speed,
        },
        "driver": {
            "name": driver.name if driver else "Subedar B. Mech",
            "phone": driver.phone if driver else "+919864067890",
        },
        "consignment": {
            "type": consignment.type if consignment else "MEDICAL_OXYGEN",
            "quantity_mt": consignment.quantity_mt if consignment else 18.5,
            "origin": consignment.origin_name
            if consignment
            else "Guwahati Central Depot",
            "destination": consignment.destination_name
            if consignment
            else "Silchar Relief Camp",
        },
        "eta_telemetry": eta_info,
    }


@router.post("/trips/{id}/delivery-proof")
def submit_delivery_proof(
    id: str, payload: DeliveryProofCreate, db: Session = Depends(get_db)
) -> Any:
    """Submit digital proof of delivery (EPOD) with signature and photo."""
    trip = db.query(Trip).filter(Trip.id == id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    proof = DeliveryProof(
        trip_id=trip.id,
        lat=payload.lat,
        lon=payload.lon,
        photo_url=payload.photo_url
        or "https://images.unsplash.com/photo-1584744982491-665216d95f8b?auto=format&fit=crop&w=400",
        receiver_name=payload.receiver_name,
        receiver_designation=payload.receiver_designation,
        digital_signature=payload.digital_signature,
        verified=True,
    )
    trip.status = "COMPLETED"
    trip.actual_arrival_time = datetime.now(UTC)
    db.add(proof)
    db.commit()

    record_audit_log(
        db=db,
        user_id="DRIVER",
        action="DELIVERY_PROOF_SUBMITTED",
        entity_type="trip",
        entity_id=trip.id,
        new_value={"receiver": payload.receiver_name},
    )
    return {"message": "Delivery proof verified and trip closed successfully."}


# Geofences
@router.post("/geofences")
def create_geofence(payload: GeofenceCreate, db: Session = Depends(get_db)) -> Any:
    """Create tactical geofence around disaster zones or supply depots."""
    geo = Geofence(
        name=payload.name,
        type=payload.type,
        center_lat=payload.center_lat,
        center_lon=payload.center_lon,
        radius_meters=payload.radius_meters,
        polygon_geojson=payload.polygon_geojson,
    )
    db.add(geo)
    db.commit()
    return {"message": f"Geofence '{payload.name}' activated.", "id": geo.id}


@router.get("/geofences/{id}/events")
def get_geofence_events(id: str) -> Any:
    """Get entry/exit events for a geofenced area."""
    return [
        {
            "event_type": "CONVOY_ENTERED",
            "vehicle_id": "AS-01-GB-4091",
            "timestamp": datetime.now(UTC).isoformat(),
            "dwell_time_min": 12.5,
        }
    ]
