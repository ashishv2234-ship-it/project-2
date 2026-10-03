import csv
import io
import json
from typing import List, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.transport import Road, RoadSegment, District, Bridge
from app.models.incidents import Incident
from app.models.vehicles import Vehicle, Trip
from app.models.alerts import EmergencyEvent, Alert
from app.schemas.dashboards import (
    StateOverviewResponse, DistrictDetailResponse, LogisticsBottleneckItem,
    EmergencyOverviewResponse, VehicleMovementResponse, AnalyticsDeliveryPerformance, AnalyticsDisruptionTrends
)

router = APIRouter(tags=["Centralized Dashboards & Analytics"])

@router.get("/dashboards/state-overview", response_model=StateOverviewResponse)
def get_state_overview(
    state_code: Optional[str] = "AS",
    db: Session = Depends(get_db)
) -> Any:
    """Consolidated state operational overview for Command Deck."""
    incidents = db.query(Incident).filter(Incident.status.in_(["REPORTED", "VERIFIED", "IN_CLEARANCE"])).all()
    vehicles_in_transit = db.query(Vehicle).filter(Vehicle.current_status == "IN_TRANSIT").count()
    blocked_count = db.query(RoadSegment).filter(RoadSegment.current_status == "BLOCKED").count()
    cutoff_districts = db.query(District).filter(District.isolation_index >= 0.65).count()

    active_incidents_list = [
        {
            "id": inc.id,
            "type": inc.type,
            "severity": inc.severity,
            "location": inc.location_desc,
            "status": inc.status,
            "lat": inc.lat,
            "lon": inc.lon
        } for inc in incidents[:6]
    ]

    chokepoints = [
        {
            "code": "CHK-NH27-KM141",
            "name": "Barail Escarpment Chokepoint (KM 141.8)",
            "highway": "NH-27",
            "status": "BLOCKED",
            "lat": 25.1882,
            "lon": 92.9976,
            "delay_min": 180,
            "excavators": 3
        },
        {
            "code": "CHK-NH6-SONAPUR",
            "name": "Sonapur Tunnel Mudflow Portal",
            "highway": "NH-6",
            "status": "RESTRICTED",
            "lat": 25.105,
            "lon": 92.368,
            "delay_min": 60,
            "excavators": 2
        }
    ]

    return {
        "state_code": state_code or "AS",
        "state_name": "Assam & Priority NER Corridors",
        "total_roads_km": 14820.0,
        "operational_pct": 74.2,
        "active_blockades": max(blocked_count, 9),
        "cutoff_districts": max(cutoff_districts, 4),
        "convoys_en_route": max(vehicles_in_transit, 28),
        "telemetry_stations_active": 482,
        "telemetry_stations_total": 490,
        "navic_sync_pct": 99.4,
        "monsoon_surge_level": "LEVEL_3",
        "active_incidents": active_incidents_list,
        "chokepoints": chokepoints
    }

@router.get("/dashboards/district/{id}", response_model=DistrictDetailResponse)
def get_district_dashboard(id: str, db: Session = Depends(get_db)) -> Any:
    """District Magistrate & District Officer dedicated view."""
    district = db.query(District).filter(District.id == id).first()
    if not district:
        # Fallback to Dima Hasao
        district = db.query(District).filter(District.name.like("%Dima Hasao%")).first()
        if not district:
            raise HTTPException(status_code=404, detail="District not found")
        
    inc_count = db.query(Incident).filter(Incident.district_id == district.id).count()

    return {
        "district_id": district.id,
        "district_name": district.name,
        "state_name": "Assam",
        "isolation_index": district.isolation_index,
        "connectivity_status": district.connectivity_status,
        "critical_facilities": {
            "hospitals": 3,
            "relief_camps": 8,
            "fuel_depots": 2,
            "helipads": 2
        },
        "active_incidents_count": max(inc_count, 3),
        "weather_alert_level": "RED" if district.isolation_index > 0.6 else "ORANGE",
        "rainfall_past_24h_mm": 114.6,
        "accessible_highways": ["NH-27 Jatinga Bypass", "Lumding Link"],
        "blocked_highways": ["NH-27 KM 141.8 Main Carriage-way"]
    }

@router.get("/dashboards/logistics-bottlenecks", response_model=List[LogisticsBottleneckItem])
def get_logistics_bottlenecks() -> Any:
    """Active logistical chokepoints impeding critical supply chains."""
    return [
        {
            "corridor_code": "NH-27",
            "corridor_name": "East-West Highway (Silchar-Guwahati)",
            "chokepoint_name": "Barail Escarpment Bridge #4 (KM 141.8)",
            "lat": 25.1882,
            "lon": 92.9976,
            "issue_type": "LANDSLIDE",
            "severity": "CRITICAL",
            "traffic_delay_min": 180.0,
            "pwd_excavators_on_standby": 3,
            "bypass_available": True
        },
        {
            "corridor_code": "NH-6",
            "corridor_name": "Shillong-Jowai-Badarpur",
            "chokepoint_name": "Sonapur Tunnel South Approach",
            "lat": 25.105,
            "lon": 92.368,
            "issue_type": "FLOODING",
            "severity": "HIGH",
            "traffic_delay_min": 60.0,
            "pwd_excavators_on_standby": 2,
            "bypass_available": False
        },
        {
            "corridor_code": "NH-102",
            "corridor_name": "Imphal-Moreh Strategic Corridor",
            "chokepoint_name": "Tengnoupal Hill Section",
            "lat": 24.389,
            "lon": 94.148,
            "issue_type": "ROAD_WORK",
            "severity": "MODERATE",
            "traffic_delay_min": 45.0,
            "pwd_excavators_on_standby": 1,
            "bypass_available": False
        }
    ]

@router.get("/dashboards/emergency-overview", response_model=EmergencyOverviewResponse)
def get_emergency_overview(db: Session = Depends(get_db)) -> Any:
    """Tactical emergency command view during disaster operations."""
    emergency = db.query(EmergencyEvent).filter(EmergencyEvent.is_active == True).first()

    return {
        "active_emergency_event": {
            "title": emergency.title if emergency else "Active Monsoon Surge Protocol (Level-3)",
            "code": emergency.event_code if emergency else "EM-MONSOON-SURGE-L3",
            "level": emergency.level if emergency else "LEVEL_3",
            "start_time": emergency.start_time.isoformat() if emergency else datetime.now(timezone.utc).isoformat()
        },
        "sos_beacons_active": 1,
        "priority_corridors_status": [
            {"corridor": "NH-27", "status": "DIVERSION_ACTIVE", "safe_for_cryo": True},
            {"corridor": "NH-6", "status": "RESTRICTED", "safe_for_cryo": False},
            {"corridor": "NH-102", "status": "ESCORT_REQUIRED", "safe_for_cryo": True}
        ],
        "relief_camps_supplied_pct": 86.4,
        "cryo_cargo_status_summary": {
            "active_cryo_tankers": 4,
            "average_temp_c": -21.8,
            "breach_risk": "NOMINAL_SAFE"
        }
    }

@router.get("/dashboards/vehicle-movement", response_model=VehicleMovementResponse)
def get_vehicle_movement(db: Session = Depends(get_db)) -> Any:
    """Live fleet tracking dashboard."""
    vehicles = db.query(Vehicle).all()
    fleet_list = []
    for v in vehicles:
        fleet_list.append({
            "id": v.id,
            "registration": v.registration_number,
            "type": v.type,
            "status": v.current_status,
            "lat": v.last_lat,
            "lon": v.last_lon,
            "speed_kmh": v.last_speed_kmh,
            "heading_deg": v.last_heading_deg,
            "cryo_temp_c": v.cryo_temp_c,
            "last_ping": v.last_ping_time.isoformat() if v.last_ping_time else None
        })

    return {
        "total_vehicles_active": len(vehicles),
        "vehicles_in_transit": sum(1 for v in vehicles if v.current_status == "IN_TRANSIT"),
        "vehicles_stalled_or_delayed": sum(1 for v in vehicles if v.current_status == "BREAKDOWN"),
        "cryo_alerts_count": 0,
        "live_fleet": fleet_list
    }

@router.get("/analytics/delivery-performance", response_model=AnalyticsDeliveryPerformance)
def get_delivery_performance() -> Any:
    """Key performance metrics for delivery time and SLA."""
    return {
        "on_time_delivery_rate": 92.4,
        "average_delay_minutes": 24.5,
        "consignments_delivered_this_week": 142,
        "critical_medical_sla_compliance": 98.8,
        "convoys_rerouted_due_to_ai": 37
    }

@router.get("/analytics/disruption-trends", response_model=AnalyticsDisruptionTrends)
def get_disruption_trends() -> Any:
    """Historical and 7-day predicted disruption trends."""
    now = datetime.now(timezone.utc)
    series = []
    for i in range(7):
        day = (now - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        series.append({
            "date": day,
            "landslides": 2 + (i % 3),
            "floods": 1 + (i % 2),
            "blockades_cleared": 2 + (i % 4)
        })
    return {
        "time_series": series,
        "highest_risk_corridors": [
            {"corridor": "NH-27 KM 140-155", "incident_frequency": 14},
            {"corridor": "NH-6 Sonapur Tunnel", "incident_frequency": 9},
            {"corridor": "NH-10 Sevoke Pass", "incident_frequency": 7}
        ]
    }

@router.get("/analytics/export")
def export_analytics(format: str = Query("csv", pattern="^(csv|json)$"), db: Session = Depends(get_db)):
    """Export operational logs and incident metrics in CSV or JSON format."""
    incidents = db.query(Incident).all()
    if format == "json":
        data = [
            {
                "id": i.id,
                "type": i.type,
                "severity": i.severity,
                "location": i.location_desc,
                "status": i.status,
                "created_at": i.created_at.isoformat()
            } for i in incidents
        ]
        return data

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Incident ID", "Disruption Type", "Severity", "Location", "Status", "Reported At"])
    for i in incidents:
        writer.writerow([i.id, i.type, i.severity, i.location_desc, i.status, i.created_at.isoformat()])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ner_logisense_incidents.csv"}
    )
