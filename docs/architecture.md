# NER-LogiSense: System Architecture Specification

## 1. Executive Summary & Architectural Vision
**NER-LogiSense** is a mission-critical, AI-powered Smart Logistics and Accessibility Intelligence Platform designed for the extreme terrain and climate vulnerabilities of India's North Eastern Region (NER) comprising 8 states (Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, Sikkim).

The region faces frequent flash floods (Brahmaputra and Barak basins), severe landslides during the South-West Monsoon, structural bridge degradation, seismic vulnerability (Zone V), and severe network connectivity blackouts. NER-LogiSense provides real-time accessibility intelligence, predictive disruption forecasting, multi-criteria route optimization, high-throughput GPS tracking of critical commodities (cryogenic medical oxygen, vaccines, foodgrains, and NDRF relief toolkits), and offline-first field hazard reporting.

---

## 2. End-to-End System Architecture

```mermaid
flowchart TB
    subgraph ClientLayer["Edge & Client Layer"]
        C1["Command Wall / Desktop Ops Deck (Chrome/Edge)"]
        C2["Rugged Field Tablets (Android / PWA Offline)"]
        C3["Driver In-Cab HUD & Telemetry Unit (NavIC L5)"]
        C4["Emergency Distress Beacons (SOS VHF/2G Burst)"]
    end

    subgraph IngressLayer["Edge Gateways & Ingress"]
        GW["Kong / Cloudflare API Gateway (Rate Limiter, TLS 1.3 Term, WAF)"]
        WSG["WebSocket / SSE Edge Gateway (Live Telemetry & Alert Stream)"]
    end

    subgraph ServiceMesh["Microservices & Domain Layer"]
        AUTH["Auth & Identity Service (OAuth 2.0 / JWT / RBAC)"]
        ACC["Network Accessibility & GIS Service (PostGIS / OGC)"]
        PRED["AI Disruption Prediction Service (XGBoost / LightGBM)"]
        OPT["Dynamic Route Optimizer Service (Time-Dependent Risk A*)"]
        FLEET["Fleet & Telemetry Ingestion Service (5,000 pts/sec)"]
        SYNC["Offline-First Sync Engine (Append-Only Queue, UUIDs)"]
        ALERT["Alert Classification & Multilingual Dispatch"]
        DASH["Dashboards & Executive Analytics Service"]
    end

    subgraph DataLayer["Storage & Cache Tier"]
        PG[("PostgreSQL 16 + PostGIS (Spatial Topology & Master Data)")]
        REDIS[("Redis 7.2 Cluster (Session Cache, Geo-Spatial Index, Pub/Sub)")]
        TIME[("TimescaleDB (High-Frequency Vehicle Telemetry)")]
        S3[("S3 / MinIO Object Storage (Geo-Tagged Damage Media & Signatures)")]
        KAFKA[["Apache Kafka / Redpanda (GPS Telemetry & Event Streaming)")]
    end

    subgraph ExternalIntegrations["External Telemetry & Government Systems"]
        IMD["IMD National Weather Network (Doppler Radar & AWS)"]
        BHUVAN["ISRO Bhuvan (OGC WMS/WFS Road Layers & CartoDEM)"]
        PWD["State PWD / BRO (Border Roads Org Infrastructure API)"]
        SMS["National Emergency SMS / Telephony Gateway"]
    end

    C1 --> GW
    C2 --> GW
    C3 --> GW
    C4 --> WSG
    C1 <--> WSG

    GW --> AUTH
    GW --> ACC
    GW --> PRED
    GW --> OPT
    GW --> FLEET
    GW --> SYNC
    GW --> ALERT
    GW --> DASH

    FLEET --> KAFKA
    KAFKA --> FLEET
    FLEET --> TIME
    ACC --> PG
    OPT --> PG
    SYNC --> PG
    AUTH --> REDIS
    ALERT --> REDIS

    PRED --> IMD
    ACC --> BHUVAN
    ACC --> PWD
    ALERT --> SMS
    SYNC --> S3
```

---

## 3. Layered Design Principles

### 3.1. Utilitarian Reliability & Zero-Downtime Resilience
- **Stateless Application Servers:** All backend instances (FastAPI ASGI) run statelessly in Kubernetes pods behind horizontal pod autoscalers (HPA).
- **Graceful Third-Party Degradation:** If external IMD or Bhuvan services experience outages, the platform falls back to cached terrain DEM profiles and historical micro-climate rainfall baselines without interrupting route planning.
- **Partitioned Resilience:** In the event of a state-wide telecom blackout (common in Dima Hasao or Champhai), the on-device SQLite database and append-only sync queue preserve local routing and hazard reporting.

### 3.2. Data Locality & Low Latency
- Redis caches active road segment states and vehicle latest pings to guarantee p95 dashboard read latencies < 180 ms.
- Dynamic route planning completes in < 800 ms using pre-compiled topological contraction hierarchies and localized subgraphs.

---

## 4. Key Data Flows

### 4.1. Real-time Telemetry Ingestion Flow (5,000 pings/sec)
1. In-cab telematics or mobile units transmit batch GPS packets with NavIC satellite coordinates, heading, speed, engine temp, and cryogenic cargo temperature.
2. Ingress gateway routes packets to the **Fleet Telemetry Ingestion Service**.
3. Service performs immediate schema validation and pushes readings into a Kafka/Redpanda topic `telemetry.gps.raw`.
4. Stream workers consume from Kafka:
   - Check against `AnomalyDetectionService` (speeding on ghat sections, breakdown, temperature breach, tampering).
   - Update vehicle current state in Redis Geo.
   - Bulk insert readings into `TimescaleDB` / `PostGIS` hypertables using chunked copy.
   - Broadcast live coordinates via WebSocket channel `/ws/telemetry` to active command screens.

### 4.2. Disruption Detection to Emergency Reroute Flow
1. An on-site BRO field officer or citizen reports a road blockage via the offline-ready field interface.
2. The report syncs via `/api/v1/sync/queue` with client UUID, geotag, accuracy, and camera photo.
3. System flags the incident as `REPORTED`, attaches automated weather radar observations, and assigns a verification task to the District Officer.
4. Upon verification, the `RoadSegment` status transitions to `BLOCKED`.
5. An automated trigger notifies the `RouteOptimizerService` to check all active trips traversing that corridor.
6. The service recalculates optimal bypass routes (e.g. NH-27 via Jatinga Bypass), calculates new ETAs, and pushes dynamic reroute alerts directly to drivers' HUDs and dispatchers' consoles.
