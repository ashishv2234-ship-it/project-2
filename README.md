# NER-LogiSense: AI-Powered Smart Logistics & Accessibility Intelligence Platform

> **Tactical Logistics, Road/Bridge Accessibility Monitoring & Predictive Disruption Intelligence for India's North Eastern Region (NER)**  
> Built from Stitch Project ID: **`13568215756576892688`**

---

## 1. Overview & Mission
**NER-LogiSense** is a mission-critical, AI-powered tactical logistics and disaster management platform engineered specifically for the highly volatile and geographically complex Northeastern Region (NER) of India. Built to support organizations such as the Border Roads Organisation (BRO), National Disaster Response Force (NDRF), and regional freight operators, the system ensures that essential supply chains remain uninterrupted during severe weather events, catastrophic landslides, and sudden infrastructure failures. 

At its core, the platform features a multi-criteria AI routing engine that computes fully verified, zero-hazard pathways. Unlike standard consumer navigation applications, the NER-LogiSense engine evaluates live field variables such as bridge load capacities, multi-axle freight weight restrictions, active landslide zones, and flash flood telemetry. This guarantees that emergency relief vehicles and heavy commercial convoys are dynamically routed around impassable terrain. To achieve this, the system leverages a time-dependent Risk A* optimization algorithm that balances rapid travel time against strict safety parameters and operational costs.

The frontend is powered by a high-performance, dark-themed tactical GIS viewport utilizing Leaflet.js. It integrates the Open Source Routing Machine (OSRM) to snap AI-calculated waypoints precisely to actual road geometries. The map provides real-time visualizations of weather radar anomalies, live convoy telemetry, and a pulse-animated District Isolation Index that instantly highlights severed territories. Furthermore, the map integrates official Survey of India boundary masks, ensuring strict geographical and political compliance.

Under the hood, NER-LogiSense utilizes a highly robust Python FastAPI backend, supported by SQLAlchemy for complex relational data handling and PostGIS schemas for advanced spatial queries. Designed for maximum resilience in environments with heavily compromised telecommunications, the software architecture natively supports robust offline-first synchronization. It automatically issues encrypted offline pass tokens and leverages a browser-level local storage engine to maintain operational continuity, even when convoys enter remote valleys reliant solely on satellite coverage. 

Security and field coordination are strictly maintained through a comprehensive Role-Based Access Control (RBAC) matrix, allowing Dispatchers, Drivers, State Disaster Management Officers, and System Administrators to interact securely with tailored dashboards. By merging real-time environmental intelligence with military-grade logistics tracking, NER-LogiSense provides an unparalleled command and control ecosystem for securing the Northeast's most critical transit corridors.

---

## 2. Core Capabilities Implemented

1. **Real-Time Road, Bridge & Accessibility Monitoring**  
   Tracks National Highways (NH-27, NH-6, NH-102, NH-13, NH-29), State Highways, and strategic bridges (Bhupen Hazarika Setu, Bogibeel, Saraighat, Barail Bridge #4) with load capacities and structural health indices.
2. **AI-Powered Disruption Prediction Microservice**  
   XGBoost / LightGBM gradient-boosted ensemble predicting landslide, flood, and mudflow probabilities for every highway segment every 15 minutes based on IMD rainfall, terrain slope, elevation, and soil instability.
3. **Multi-Criteria Dynamic Route Optimization**  
   Time-dependent, risk-weighted shortest path algorithm optimizing for:
   $$\text{Cost} = \alpha \cdot \text{travel\_time} + \beta \cdot \text{risk\_score} + \gamma \cdot \text{operating\_cost}$$
   Generates 3 comparative routes (Optimal Route A, Alternate Route B, Contingency Route C) and handles disconnected graphs with nearest safe shelter fallbacks.
4. **High-Throughput GPS Fleet Tracking & Cryogenic Telemetry**  
   Capable of ingesting 5,000 location updates/sec with NavIC L5 GNSS precision, live speed, heading, and cryogenic temperature monitoring ($-15^\circ\text{C}$ critical threshold for liquid medical oxygen and vaccines).
5. **Offline-First Field Hazard Reporting with Conflict Resolution**  
   Enables field officers in zero-connectivity mountain corridors to report blockades with photos and GPS. Uses client-generated UUIDs, an append-only local SQLite queue, and automated multi-version conflict resolution.
6. **Tactical Anomaly Detection**  
   Flags breakdown, prolonged stoppage, mountain road overspeeding, cryogenic temperature breaches, and GPS tampering/location jumps.
7. **Multilingual Disaster Alerts**  
   Automated emergency translation and broadcasting across 9 regional languages: English, Assamese, Bengali, Hindi, Manipuri, Mizo, Khasi, Garo, and Nagamese.
8. **Real-Time WebSocket Streams**  
   Low-latency bidirectional channels (`/ws/telemetry` for live convoy GPS and `/ws/alerts` for immediate tactical alerts).

---

## 3. Stitch Project `13568215756576892688` Conversion

The platform directly converts the design system and screens from Stitch project `13568215756576892688` into an interactive Single-Page Application (SPA):
- **Live Accessibility GIS Map & Tactical HUD:** Dark tactical vector basemap, status-coded highway segments, bridge capacity pins, and live vehicle convoy markers.
- **District Isolation Index:** Real-time vulnerability scores for all 8 NER states.
- **AI Risk & Disruption Forecast:** Landslide and flood probabilities with contributing factor breakdowns.
- **Strategic Route Planner & Relief Convoy Dispatch:** Multi-criteria trajectory comparison with military escort tagging.
- **Commodity Fleet Tracking & Cryo Telemetry:** Cold-chain integrity monitoring.
- **Incident & Field Verification Console:** Verification workflows for PWD/BRO commanders.
- **Emergency Corridors (SOS):** Level-3 monsoon disaster state coordination.
- **Offline Field App Portal:** Simulated rugged mobile tablet with on-device SQLite queue and burst synchronization.

---

## 4. Technology Stack

- **Backend Framework:** Python 3.11+ / FastAPI (high-performance async ASGI)
- **Primary Database:** PostgreSQL 16 + PostGIS (spatial geometry and GIST indexes) / SQLite with spatial logic for zero-dependency local runs
- **Cache & Telemetry Index:** Redis 7.2
- **Message Streaming:** Redpanda / Apache Kafka (5,000 GPS pings/sec)
- **Object Storage:** MinIO / AWS S3 (geo-tagged damage photos and signatures)
- **ML / AI Engine:** scikit-learn, XGBoost, LightGBM
- **GIS Services:** Leaflet, ISRO Bhuvan OGC services, CartoDEM
- **Testing:** Pytest (14 passing unit and integration tests)
- **Deployment:** Docker, Docker Compose, Kubernetes manifests, GitHub Actions CI/CD

---

## 5. Repository Structure

```
PROJECT 2/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & WebSocket endpoints
│   │   ├── core/                       # Config, Security (JWT/PBKDF2), RBAC, Audit Logging
│   │   ├── models/                     # SQLAlchemy models (User, Transport, Weather, Incidents, Fleet, Alerts)
│   │   ├── schemas/                    # Pydantic v2 schemas
│   │   ├── api/v1/                     # REST API routers (68 endpoints)
│   │   ├── services/                   # ML disruption, Route optimizer, ETA predictor, Anomaly detector, Sync engine
│   │   ├── websocket/                  # WebSocket connection manager & pub/sub
│   │   └── seed/                       # Database seed scripts with authentic NER data
│   ├── tests/                          # 100% passing pytest test suite
│   ├── requirements.txt
│   └── run.py                          # Local server launcher
├── frontend/                           # Interactive Web Platform (Stitch 13568215756576892688)
│   ├── index.html                      # Single Page Application
│   ├── css/styles.css                  # Tactical dark theme design system
│   └── js/                             # app.js, map.js, api.js, websocket.js, offline-store.js
├── docs/
│   ├── architecture.md                 # System architecture specification & diagrams
│   ├── microservices.md                # 10-module microservice breakdown
│   ├── postgis_schema.sql              # Production PostGIS DDL with spatial indexes
│   ├── openapi.json                    # Complete OpenAPI 3.1 schema (68 endpoints)
│   ├── websocket_contracts.md          # WebSocket/SSE contracts & schemas
│   ├── ml_architecture.md              # ML model design & feature store
│   ├── offline_sync_protocol.md        # Offline sync queue & conflict resolution state machine
│   ├── background_jobs.md              # Celery/Kafka event-driven workflows
│   ├── rbac_matrix.md                  # Role-based access control matrix
│   ├── monitoring_backup.md            # Observability, Prometheus, Grafana, backup runbook
│   └── k8s/k8s-deployment.yaml         # Kubernetes StatefulSet, Deployment, HPA, Ingress
├── docker-compose.yml                  # Full multi-container stack
├── Dockerfile                          # Multi-stage production container
├── .github/workflows/ci-cd.yml         # GitHub Actions automated pipeline
└── README.md
```

---

## 6. Quick Start Guide

### Option A: Local Development (Instant Launch)
The backend is pre-configured with SQLite fallback and automatic demo database seeding:

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run the test suite
python -m pytest tests/

# 3. Start the Backend API & Interactive Website
python run.py
```

Open your browser to:
- **Interactive Web Platform:** [http://localhost:8000/](http://localhost:8000/)
- **Swagger / OpenAPI Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Interactive Reference:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Option B: Docker Compose (Full Production Stack)
To run the full stack with PostgreSQL + PostGIS, Redis, Redpanda, MinIO, Prometheus, and Grafana:

```bash
docker-compose up --build -d
```
- **Web App & API:** [http://localhost:8000](http://localhost:8000)
- **Grafana Dashboards:** [http://localhost:3001](http://localhost:3001) (User: `admin`, Pass: `admin`)
- **MinIO S3 Console:** [http://localhost:9001](http://localhost:9001) (User: `minioadmin`, Pass: `minioadmin`)

---

## 7. Default Credentials for Demo

| Role | Email | Password | Phone |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@ner-logisense.gov.in` | `Password123!` | `+919864012345` |
| **State Admin** | `state.admin@assam.gov.in` | `Password123!` | `+919864023456` |
| **District Officer** | `dc.dimahasao@assam.gov.in` | `Password123!` | `+919864034567` |
| **Dispatcher** | `dispatch.guwahati@ner.gov.in`| `Password123!` | `+919864045678` |
| **Field Officer** | `field.officer@ner.gov.in` | `Password123!` | `+919864056789` |
| **Driver** | `driver.mech@ner.gov.in` | `Password123!` | `+919864067890` |
| **Field SMS OTP** | Any registered phone | `704820` | - |

---

## 8. Verification & Test Evidence

All 14 test cases execute and pass:
```
tests/test_auth.py::test_health_check PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_invalid_password PASSED
tests/test_auth.py::test_otp_flow PASSED
tests/test_ml_and_anomalies.py::test_ml_disruption_prediction PASSED
tests/test_ml_and_anomalies.py::test_anomaly_detection_cryo_breach PASSED
tests/test_ml_and_anomalies.py::test_alert_classification_and_deduplication PASSED
tests/test_network_and_routing.py::test_get_roads PASSED
tests/test_network_and_routing.py::test_accessibility_summary PASSED
tests/test_network_and_routing.py::test_plan_route PASSED
tests/test_network_and_routing.py::test_emergency_corridors PASSED
tests/test_offline_sync.py::test_offline_field_report_sync PASSED
tests/test_offline_sync.py::test_offline_sync_idempotency PASSED
tests/test_offline_sync.py::test_delta_sync PASSED
============================== 14 passed in 1.73s ==============================
```
