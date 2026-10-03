# NER-LogiSense: Microservice & Module Breakdown

This document describes the functional scope, internal interfaces, database access boundaries, and scaling models of each core microservice module within NER-LogiSense.

---

## 1. Identity & Access Management (IAM)
- **Primary Responsibility:** User lifecycle, authentication (OAuth 2.0 / JWT), OTP generation for remote field personnel, and hierarchical role-based authorization.
- **Roles Governed:** Super Admin, State Admin, District Officer, Field Officer, Dispatcher, Driver, Viewer.
- **Key APIs:** `/api/v1/auth/*`, `/api/v1/users/*`
- **Data Stores:** `users`, `audit_logs`
- **Security Protocols:** PBKDF2-HMAC-SHA256 password hashing, RS256/HS256 short-lived access tokens (60 min) with refresh tokens (7 days), IP logging on all administrative actions.

---

## 2. GIS & Network Topology Service
- **Primary Responsibility:** Manages spatial graph topology of all National Highways (NH), State Highways (SH), Border Roads (BRO), and rural connectors across the 8 NER states. Maintains bridge load capacities, ferry crossings, checkpoints, and helipads.
- **Key APIs:** `/api/v1/network/*`
- **Data Stores:** `states`, `districts`, `roads`, `road_segments`, `bridges`, `infrastructure_nodes`, `road_status_events`
- **GIS Integrations:** PostGIS spatial indexing (`ST_DWithin`, `ST_Intersects`), ISRO Bhuvan OGC WMS/WFS map tiles, and CartoDEM elevation rasters.

---

## 3. Weather & Hazard Monitoring Service
- **Primary Responsibility:** Ingests real-time observations and forecasts from IMD AWS stations and Doppler radars located in Guwahati, Mohanbari, Cherrapunji, and Agartala. Maps precipitation thresholds against flood catchment basins.
- **Key APIs:** `/api/v1/weather/*`
- **Data Stores:** `weather_observations`, `weather_forecasts`, `flood_risk_zones`, `landslide_risk_zones`
- **Alert Levels:** GREEN (Normal), YELLOW (Advisory), ORANGE (Preparedness), RED (Imminent Disaster).

---

## 4. AI Disruption Prediction Microservice
- **Primary Responsibility:** Computes probabilistic risk of landslides, mudflows, flash floods, and bridge damage for every individual highway segment every 15 minutes.
- **Key APIs:** `/api/v1/risk/*`
- **Model Engine:** Python FastAPI microservice utilizing scikit-learn, XGBoost, and LightGBM.
- **Inputs:** 24h accumulated rainfall, 24h predictive rainfall, hill slope degrees, terrain elevation, soil instability type (loose shale, weathered sandstone), historical failure density, and live field reports.
- **Output:** Risk probability $[0.0, 1.0]$, severity classification, expected clearance duration, and confidence index.

---

## 5. Multi-Criteria Route Optimization Engine
- **Primary Responsibility:** Time-dependent, risk-weighted shortest path calculation on dynamic graphs.
- **Cost Formula:**
  $$\text{Cost} = \alpha \cdot \text{travel\_time} + \beta \cdot \text{risk\_score} + \gamma \cdot \text{operating\_cost}$$
- **Key APIs:** `/api/v1/routes/*`
- **Priority Profiles:**
  - **SAFEST:** Minimizes landslide and flood probability ($\beta = 0.60$).
  - **FASTEST:** Optimizes overall transit hours ($\alpha = 0.70$).
  - **LOW_DISRUPTION:** Maximizes probability of completing journey without encountering roadblock.
  - **HEAVY_CLEARANCE:** Avoids low-capacity bridges ($<40\text{ MT}$) and excessive slope gradients.
  - **EMERGENCY:** Fast-tracks military, medical oxygen, and NDRF disaster convoys with police escort tagging.
- **Disconnected Graph Fallback:** Automatically calculates nearest accessible safe shelter, army cantonment, or relief depot when target destination is cut off.

---

## 6. Fleet Tracking & Telemetry Stream Engine
- **Primary Responsibility:** High-throughput ingestion of 5,000 GPS points per second, vehicle telematics (NavIC satellite counts, speed, ignition, engine temperature, and cryogenic cold-chain sensors).
- **Key APIs:** `/api/v1/vehicles/*`, `/api/v1/consignments/*`, `/api/v1/trips/*`, `/api/v1/geofences/*`, WebSocket `/ws/telemetry`
- **Streaming Pipeline:** Kafka/Redpanda $\to$ TimescaleDB $\to$ Redis Geo Cache $\to$ WebSocket Broadcast.

---

## 7. Incident & Field Verification Service
- **Primary Responsibility:** Lifecycle management of real-world disruptions (landslides, bridge collapses, fallen trees, flash flood inundations). Coordinates field reporting, peer cross-checking, PWD engineering dispatch, and closure resolution.
- **Key APIs:** `/api/v1/incidents/*`, `/api/v1/field-reports/*`, `/api/v1/media/*`
- **Data Stores:** `incidents`, `field_reports`, `media_assets`, `verification_tasks`
- **Media Pipeline:** Secure SHA-256 validated upload, MIME validation, virus scanning, and AWS S3 presigned URL delivery.

---

## 8. Offline-First Synchronization Engine
- **Primary Responsibility:** Provides bidirectional sync for low-connectivity mobile clients operating in deep mountain gorges.
- **Key APIs:** `/api/v1/sync/queue`, `/api/v1/sync/delta`
- **Protocols:**
  - Client-generated UUIDs prevent double submissions.
  - Append-only sync queue preserving temporal causality.
  - Automatic conflict resolution for field reports, road statuses, and GPS logs.
  - Delta sync with `updated_at` cursors to minimize cellular bandwidth usage.

---

## 9. Alert Classification & Multilingual Dispatch
- **Primary Responsibility:** Prioritizes critical alerts, suppresses duplicates within 30-minute sliding windows, and broadcasts emergency messages across 9 regional languages.
- **Key APIs:** `/api/v1/alerts/*`, `/api/v1/notifications/*`, `/api/v1/emergency-events/*`, WebSocket `/ws/alerts`
- **Supported Languages:** English, Assamese, Bengali, Hindi, Manipuri, Mizo, Khasi, Garo, Nagamese.
- **Delivery Channels:** WebSockets, In-App Notifications, SMS Gateway, Push Notifications, WhatsApp Business API.

---

## 10. Centralized Dashboards & Analytics Service
- **Primary Responsibility:** Aggregates operational telemetry for command centers, district magistrates, and disaster relief commissioners.
- **Key APIs:** `/api/v1/dashboards/*`, `/api/v1/analytics/*`
- **Export Capabilities:** Automated export to CSV, PDF, and JSON formats for inter-departmental briefings.
