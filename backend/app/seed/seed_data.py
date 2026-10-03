import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, AuditLog
from app.models.transport import (
    State, District, Road, RoadSegment, Bridge, InfrastructureNode, RoadStatusEvent
)
from app.models.weather import (
    WeatherObservation, WeatherForecast, FloodRiskZone, LandslideRiskZone, RiskScore
)
from app.models.incidents import Incident, FieldReport, MediaAsset, VerificationTask
from app.models.vehicles import Vehicle, Driver, GPSReading, Consignment, Trip, DeliveryProof, Geofence
from app.models.routing import RouteRequest, RouteOption
from app.models.alerts import Alert, AlertSubscription, Notification, EmergencyEvent

def seed_database(db: Session = None):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        # Check if database is already seeded
        if db.query(User).filter(User.email == "admin@ner-logisense.gov.in").first():
            print("[SEED] Database already contains seed records. Skipping creation.")
            return

        print("[SEED] Initializing NER-LogiSense seed database...")
        now = datetime.now(timezone.utc)

        # 1. Users & Roles
        users_data = [
            {
                "name": "Col. R. Saikia",
                "phone": "+919864012345",
                "email": "admin@ner-logisense.gov.in",
                "role": "Super Admin",
                "district": "Kamrup Metro (Guwahati)",
                "state": "Assam",
                "language": "en"
            },
            {
                "name": "Dr. P. Barua",
                "phone": "+919864023456",
                "email": "state.admin@assam.gov.in",
                "role": "State Admin",
                "district": "Kamrup Metro (Guwahati)",
                "state": "Assam",
                "language": "as"
            },
            {
                "name": "T. Jamir, IAS",
                "phone": "+919864034567",
                "email": "dc.dimahasao@assam.gov.in",
                "role": "District Officer",
                "district": "Dima Hasao (Haflong)",
                "state": "Assam",
                "language": "en"
            },
            {
                "name": "S. Khongwir",
                "phone": "+919864045678",
                "email": "dispatch.guwahati@ner.gov.in",
                "role": "Dispatcher",
                "district": "Kamrup Metro (Guwahati)",
                "state": "Assam",
                "language": "kha"
            },
            {
                "name": "R. Debbarma",
                "phone": "+919864056789",
                "email": "field.officer@ner.gov.in",
                "role": "Field Officer",
                "district": "Dima Hasao (Haflong)",
                "state": "Assam",
                "language": "en"
            },
            {
                "name": "B. Mech",
                "phone": "+919864067890",
                "email": "driver.mech@ner.gov.in",
                "role": "Driver",
                "district": "Kamrup Metro (Guwahati)",
                "state": "Assam",
                "language": "as"
            }
        ]

        user_instances = {}
        for u in users_data:
            user = User(
                name=u["name"],
                phone=u["phone"],
                email=u["email"],
                hashed_password=hash_password("Password123!"),
                role=u["role"],
                district=u["district"],
                state=u["state"],
                language=u["language"],
                status="ACTIVE",
                created_at=now
            )
            db.add(user)
            db.flush()
            user_instances[u["email"]] = user

        # 2. States (All 8 North Eastern States)
        states_data = [
            ("Assam", "AS", "Dispur (Guwahati)"),
            ("Meghalaya", "ML", "Shillong"),
            ("Arunachal Pradesh", "AR", "Itanagar"),
            ("Nagaland", "NL", "Kohima"),
            ("Manipur", "MN", "Imphal"),
            ("Mizoram", "MZ", "Aizawl"),
            ("Tripura", "TR", "Agartala"),
            ("Sikkim", "SK", "Gangtok")
        ]
        state_instances = {}
        for sname, scode, scapital in states_data:
            state = State(name=sname, code=scode, capital=scapital)
            db.add(state)
            db.flush()
            state_instances[scode] = state

        # 3. Districts
        districts_data = [
            ("Dima Hasao (Haflong)", "AS", 0.72, "RESTRICTED", 25.188, 92.997),
            ("Kamrup Metro (Guwahati)", "AS", 0.05, "CONNECTED", 26.144, 91.736),
            ("Cachar (Silchar)", "AS", 0.45, "RESTRICTED", 24.833, 92.779),
            ("East Khasi Hills (Shillong)", "ML", 0.28, "CONNECTED", 25.578, 91.893),
            ("Champhai (Indo-Myanmar)", "MZ", 0.82, "SEVERED", 23.475, 93.328),
            ("Papum Pare (Itanagar)", "AR", 0.35, "CONNECTED", 27.102, 93.621),
            ("Kohima", "NL", 0.40, "RESTRICTED", 25.674, 94.110),
            ("Imphal West", "MN", 0.48, "RESTRICTED", 24.817, 93.936),
            ("Kalimpong / Sevoke Pass", "SK", 0.65, "RESTRICTED", 27.066, 88.473)
        ]
        district_instances = {}
        for dname, scode, is_idx, status, lat, lon in districts_data:
            dist = District(
                name=dname,
                state_id=state_instances[scode].id,
                isolation_index=is_idx,
                connectivity_status=status,
                center_lat=lat,
                center_lon=lon
            )
            db.add(dist)
            db.flush()
            district_instances[dname] = dist

        # 4. Roads & Highways
        roads_data = [
            ("National Highway 27 (East-West Strategic Corridor)", "NH-27", "NATIONAL_HIGHWAY", "ASPHALT", 4, "NHAI", "RESTRICTED"),
            ("National Highway 6 (Shillong-Jowai-Badarpur)", "NH-6", "NATIONAL_HIGHWAY", "ASPHALT", 2, "NHAI", "RESTRICTED"),
            ("National Highway 102 (Imphal-Moreh Strategic Corridor)", "NH-102", "NATIONAL_HIGHWAY", "ASPHALT", 2, "BRO", "HIGH_RISK"),
            ("Trans-Arunachal Highway", "NH-13", "NATIONAL_HIGHWAY", "ASPHALT", 2, "BRO", "OPEN"),
            ("National Highway 29 (Dimapur-Kohima Pass)", "NH-29", "NATIONAL_HIGHWAY", "ASPHALT", 2, "NHAI", "OPEN"),
            ("SH-4 Umrangso Reservoir Tactical Link", "SH-4", "STATE_HIGHWAY", "CONCRETE", 2, "STATE_PWD", "RESTRICTED")
        ]
        road_instances = {}
        for rname, rcode, rtype, rsurf, rlanes, rowner, rstatus in roads_data:
            road = Road(
                name=rname,
                code=rcode,
                type=rtype,
                surface=rsurf,
                lanes=rlanes,
                owner_department=rowner,
                status=rstatus
            )
            db.add(road)
            db.flush()
            road_instances[rcode] = road

        # 5. Road Segments
        nh27 = road_instances["NH-27"]
        nh6 = road_instances["NH-6"]
        dima_dist = district_instances["Dima Hasao (Haflong)"]

        seg1 = RoadSegment(
            road_id=nh27.id,
            district_id=dima_dist.id,
            start_point_name="Jatinga Junction",
            end_point_name="Barail Escarpment Bridge #4 (KM 141.8)",
            start_lat=25.123,
            start_lon=93.042,
            end_lat=25.188,
            end_lon=92.997,
            length_km=14.2,
            elevation_m=920.0,
            slope_degrees=42.0,
            flood_risk_score=0.25,
            landslide_risk_score=0.88,
            current_status="BLOCKED",
            current_travel_time_min=55.0,
            expected_delay_min=180.0
        )
        db.add(seg1)

        seg2 = RoadSegment(
            road_id=nh27.id,
            district_id=district_instances["Kamrup Metro (Guwahati)"].id,
            start_point_name="Guwahati Central Depot",
            end_point_name="Nagaon Bypass",
            start_lat=26.182,
            start_lon=91.758,
            end_lat=26.345,
            end_lon=92.684,
            length_km=122.0,
            elevation_m=65.0,
            slope_degrees=4.0,
            flood_risk_score=0.35,
            landslide_risk_score=0.05,
            current_status="OPEN",
            current_travel_time_min=120.0,
            expected_delay_min=0.0
        )
        db.add(seg2)

        seg3 = RoadSegment(
            road_id=nh6.id,
            district_id=district_instances["East Khasi Hills (Shillong)"].id,
            start_point_name="Jowai Mountain Link",
            end_point_name="Sonapur Tunnel Section",
            start_lat=25.448,
            start_lon=92.203,
            end_lat=25.105,
            end_lon=92.368,
            length_km=48.5,
            elevation_m=1240.0,
            slope_degrees=38.0,
            flood_risk_score=0.60,
            landslide_risk_score=0.74,
            current_status="RESTRICTED",
            current_travel_time_min=95.0,
            expected_delay_min=60.0
        )
        db.add(seg3)
        db.flush()

        # 6. Strategic Bridges
        bridges_data = [
            ("Bhupen Hazarika Setu (Dhola-Sadiya)", nh27.id, 27.797, 95.666, 60.0, "OPERATIONAL", 98.0),
            ("Bogibeel Rail-Road Bridge", nh27.id, 27.404, 94.922, 60.0, "OPERATIONAL", 99.0),
            ("Saraighat Bridge (Brahmaputra)", nh27.id, 26.128, 91.681, 45.0, "OPERATIONAL", 94.0),
            ("Barail Escarpment Bridge #4 (KM 141.8)", nh27.id, 25.188, 92.997, 40.0, "WEIGHT_RESTRICTED", 76.5),
            ("Sonapur Tunnel Aqueduct & Viaduct", nh6.id, 25.105, 92.368, 35.0, "SUBMERGED", 62.0)
        ]
        for bname, rid, lat, lon, cap, bstatus, health in bridges_data:
            bridge = Bridge(
                name=bname,
                road_id=rid,
                lat=lat,
                lon=lon,
                load_capacity_mt=cap,
                status=bstatus,
                structural_health_index=health,
                last_inspection_date=now - timedelta(days=12)
            )
            db.add(bridge)

        # 7. Infrastructure Nodes (Warehouses, Hospitals, Helipads, Camps)
        nodes_data = [
            ("Guwahati Central Logistics Depot", "WAREHOUSE", district_instances["Kamrup Metro (Guwahati)"].id, 26.182, 91.758, "12,000 MT capacity", "+919864011111"),
            ("Silchar Medical Relief Hub", "HOSPITAL", district_instances["Cachar (Silchar)"].id, 24.833, 92.779, "500 Critical Beds + Cryo Vault", "+919864022222"),
            ("Haflong Relief Camp #1 (Highland)", "RELIEF_CAMP", dima_dist.id, 25.188, 92.997, "3,500 Displaced Persons", "+919864033333"),
            ("Jatinga Emergency Helipad", "HELIPAD", dima_dist.id, 25.118, 93.038, "Dual Mi-17 V5 Landing Pads", "+919864044444"),
            ("Lumding Army Cantonment Staging Hub", "CHECKPOINT", dima_dist.id, 25.750, 93.167, "Convoy Staging & Fuel Vault", "+919864055555")
        ]
        for nname, ntype, did, lat, lon, cap, phone in nodes_data:
            node = InfrastructureNode(
                name=nname,
                type=ntype,
                district_id=did,
                lat=lat,
                lon=lon,
                capacity_desc=cap,
                contact_phone=phone,
                is_operational=True
            )
            db.add(node)

        # 8. Drivers & Vehicles
        driver1 = Driver(
            name="Subedar B. Mech",
            phone="+919864067890",
            license_number="AS-01-2018-009182",
            blood_group="B+",
            status="ON_TRIP"
        )
        db.add(driver1)
        db.flush()

        v1 = Vehicle(
            registration_number="AS-01-GB-4091",
            type="CRYO_TANKER",
            capacity_mt=18.5,
            owner="Govt of Assam / NEC Relief Logistics",
            driver_id=driver1.id,
            current_status="IN_TRANSIT",
            last_lat=25.750,
            last_lon=93.167,
            last_speed_kmh=42.0,
            last_heading_deg=138.0,
            cryo_temp_c=-22.4, # Safe cryogenic cold-chain
            last_ping_time=now
        )
        v2 = Vehicle(
            registration_number="AS-01-EC-7104",
            type="MULTI_AXLE_HEAVY",
            capacity_mt=24.0,
            owner="FCI Eastern Logistics Fleet",
            current_status="IN_TRANSIT",
            last_lat=26.002,
            last_lon=92.865,
            last_speed_kmh=48.0,
            last_heading_deg=112.0,
            last_ping_time=now
        )
        v3 = Vehicle(
            registration_number="ML-05-AA-3120",
            type="4X4_TACTICAL_PICKUP",
            capacity_mt=5.0,
            owner="NDRF 1st Battalion Emergency Fleet",
            current_status="ACTIVE",
            last_lat=25.578,
            last_lon=91.893,
            last_speed_kmh=35.0,
            last_heading_deg=90.0,
            last_ping_time=now
        )
        db.add_all([v1, v2, v3])
        db.flush()

        # Telemetry GPS Readings for v1
        for i in range(5):
            gps = GPSReading(
                vehicle_id=v1.id,
                timestamp=now - timedelta(minutes=(4 - i) * 5),
                latitude=25.750 - (i * 0.04),
                longitude=93.167 + (i * 0.03),
                speed_kmh=40.0 + (i * 2.0),
                heading_deg=138.0,
                accuracy_m=1.8,
                altitude_m=420.0 + (i * 25.0),
                ignition_status=True,
                engine_temp_c=86.5,
                cryo_temp_c=-22.4 + (i * 0.1),
                navic_satellite_count=9
            )
            db.add(gps)

        # 9. Consignments & Trips
        consignment = Consignment(
            consignment_number="CON-NER-2026-881",
            type="MEDICAL_OXYGEN",
            description="Cryogenic Liquid Medical Oxygen (LMO) & Critical Saline",
            quantity_mt=18.5,
            origin_name="Guwahati Central Logistics Depot",
            origin_lat=26.182,
            origin_lon=91.758,
            destination_name="Haflong / Silchar Relief Camp",
            dest_lat=25.188,
            dest_lon=92.997,
            priority="GRADE_1_CRITICAL",
            temperature_requirement="-25C to -15C",
            status="IN_TRANSIT"
        )
        db.add(consignment)
        db.flush()

        trip = Trip(
            trip_code="MISSION-RELIEF-NER-704",
            vehicle_id=v1.id,
            driver_id=driver1.id,
            consignment_id=consignment.id,
            planned_route_geojson=json.dumps([
                [26.182, 91.758], [26.345, 92.684], [25.750, 93.167], [25.123, 93.042], [25.188, 92.997]
            ]),
            departure_time=now - timedelta(hours=3),
            estimated_arrival_time=now + timedelta(hours=4, minutes=45),
            status="IN_TRANSIT",
            current_delay_min=18.0
        )
        db.add(trip)

        # 10. Incidents & Hazards
        inc1 = Incident(
            type="landslide",
            severity="CRITICAL",
            location_desc="NH-27 KM 141.8, Dima Hasao Sector (Near Barail Bridge #4)",
            lat=25.1882,
            lon=92.9976,
            road_segment_id=seg1.id,
            district_id=dima_dist.id,
            description="Massive hill slope debris failure. Approximately 4,500 m3 of rock and shale spanning 80m of carriage-way. Traffic severed both directions.",
            status="VERIFIED",
            reported_by=user_instances["field.officer@ner.gov.in"].id,
            verified_by=user_instances["admin@ner-logisense.gov.in"].id,
            estimated_clearance_hours=14.0
        )
        inc2 = Incident(
            type="flood",
            severity="HIGH",
            location_desc="Sonapur Tunnel Southern Portal, NH-6 Meghalaya",
            lat=25.105,
            lon=92.368,
            road_segment_id=seg3.id,
            district_id=district_instances["East Khasi Hills (Shillong)"].id,
            description="River water overflowing portal roadway by 0.75m. Heavy mudflow deposit.",
            status="IN_CLEARANCE",
            reported_by=user_instances["field.officer@ner.gov.in"].id,
            verified_by=user_instances["state.admin@assam.gov.in"].id,
            estimated_clearance_hours=6.0
        )
        db.add_all([inc1, inc2])
        db.flush()

        # Field Report tied to Incident 1 (matching Stitch Screen 04d9309cc87e47f8bffcd0e15e74a629)
        fr1 = FieldReport(
            client_uuid="550e8400-e29b-41d4-a716-446655440000",
            incident_id=inc1.id,
            reporter_id=user_instances["field.officer@ner.gov.in"].id,
            lat=25.1882,
            lon=92.9976,
            accuracy_m=1.8,
            disruption_type="Landslide",
            severity="CRITICAL",
            description="Road completely blocked. Barail Escarpment Bridge #4 approach covered. Immediate PWD heavy excavation required.",
            media_files_json=json.dumps(["https://images.unsplash.com/photo-1545641203-7d072a14e3b7?auto=format&fit=crop&w=800"]),
            offline_created_at=now - timedelta(minutes=45),
            synced_at=now - timedelta(minutes=40),
            sync_status="SYNCED",
            device_id="RUGGED-FIELD-TAB-AS04"
        )
        db.add(fr1)

        # 11. Alerts & Notifications
        alert1 = Alert(
            type="LANDSLIDE_BLOCKADE",
            severity="CRITICAL",
            district_id=dima_dist.id,
            road_id=nh27.id,
            location_desc="NH-27 KM 141.8 Barail Escarpment",
            message="CRITICAL: NH-27 KM 141.8 severed due to 80m landslide. Jatinga Bypass diversion activated for relief convoys.",
            status="ACTIVE",
            created_at=now - timedelta(hours=1),
            expires_at=now + timedelta(hours=24)
        )
        alert2 = Alert(
            type="FLASH_FLOOD_SURGE",
            severity="HIGH",
            district_id=district_instances["East Khasi Hills (Shillong)"].id,
            road_id=nh6.id,
            location_desc="NH-6 Sonapur Tunnel Approach",
            message="HIGH RISK: Sonapur Tunnel flash flood. Single lane shuttle transit with heavy vehicle restrictions.",
            status="ACTIVE",
            created_at=now - timedelta(hours=2),
            expires_at=now + timedelta(hours=12)
        )
        db.add_all([alert1, alert2])
        db.flush()

        # Emergency Event (matching Active Monsoon Surge Protocol Level-3 banner)
        em_event = EmergencyEvent(
            event_code="EM-MONSOON-SURGE-L3",
            title="Active Monsoon Surge Protocol (Level-3)",
            type="MONSOON_SURGE",
            level="LEVEL_3",
            affected_districts_json=json.dumps([
                "Dima Hasao (Haflong)", "East Khasi Hills (Shillong)", "Cachar (Silchar)", "Champhai"
            ]),
            activated_by=user_instances["admin@ner-logisense.gov.in"].id,
            start_time=now - timedelta(days=1),
            priority_corridors_json=json.dumps(["NH-27", "NH-6", "NH-102"]),
            is_active=True
        )
        db.add(em_event)

        db.commit()
        print("[SEED] Successfully seeded NER-LogiSense with complete regional test environment!")

    except Exception as e:
        db.rollback()
        print(f"[SEED ERROR]: {e}")
        raise
    finally:
        if close_after:
            db.close()

if __name__ == "__main__":
    seed_database()
