-- ============================================================================
-- NER-LogiSense: Production PostgreSQL 16 + PostGIS Spatial Schema
-- Purpose: Tactical road network, bridges, AI risk, incidents, fleet tracking
-- Coordinate Reference System: WGS 84 (EPSG:4326)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- ----------------------------------------------------------------------------
-- 1. USERS, ROLES & AUDITING
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    hashed_password VARCHAR(256) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Viewer',
    district VARCHAR(100),
    state VARCHAR(100) DEFAULT 'Assam',
    language VARCHAR(20) DEFAULT 'en',
    status VARCHAR(30) DEFAULT 'ACTIVE',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_district ON users (district);

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_entity ON audit_logs (entity_type, entity_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs (timestamp DESC);

-- ----------------------------------------------------------------------------
-- 2. ADMINISTRATIVE BOUNDARIES & TRANSPORT SPATIAL TOPOLOGY
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL, -- AS, ML, AR, NL, MN, MZ, TR, SK
    capital VARCHAR(100) NOT NULL,
    boundary GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX idx_states_geom ON states USING GIST (boundary);

CREATE TABLE IF NOT EXISTS districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    state_id UUID NOT NULL REFERENCES states(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    isolation_index DOUBLE PRECISION DEFAULT 0.0,
    connectivity_status VARCHAR(30) DEFAULT 'CONNECTED',
    critical_facilities_count INT DEFAULT 5,
    center_geom GEOMETRY(Point, 4326),
    boundary GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX idx_districts_geom ON districts USING GIST (boundary);
CREATE INDEX idx_districts_center ON districts USING GIST (center_geom);
CREATE INDEX idx_districts_isolation ON districts (isolation_index);

CREATE TABLE IF NOT EXISTS roads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    code VARCHAR(50) NOT NULL, -- NH-27, NH-6, NH-102
    type VARCHAR(50) NOT NULL, -- NATIONAL_HIGHWAY, STATE_HIGHWAY, BRO_TACTICAL, PMGSY_RURAL
    surface VARCHAR(50) DEFAULT 'ASPHALT',
    lanes INT DEFAULT 2,
    owner_department VARCHAR(100) DEFAULT 'NHAI',
    status VARCHAR(30) DEFAULT 'OPEN',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roads_code ON roads (code);
CREATE INDEX idx_roads_status ON roads (status);

CREATE TABLE IF NOT EXISTS road_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    road_id UUID NOT NULL REFERENCES roads(id) ON DELETE CASCADE,
    district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
    start_point_name VARCHAR(100) NOT NULL,
    end_point_name VARCHAR(100) NOT NULL,
    length_km DOUBLE PRECISION NOT NULL,
    elevation_m DOUBLE PRECISION DEFAULT 300.0,
    slope_degrees DOUBLE PRECISION DEFAULT 5.0,
    flood_risk_score DOUBLE PRECISION DEFAULT 0.1,
    landslide_risk_score DOUBLE PRECISION DEFAULT 0.1,
    current_status VARCHAR(30) DEFAULT 'OPEN',
    speed_limit_kmh DOUBLE PRECISION DEFAULT 60.0,
    current_travel_time_min DOUBLE PRECISION DEFAULT 15.0,
    expected_delay_min DOUBLE PRECISION DEFAULT 0.0,
    start_point GEOMETRY(Point, 4326) NOT NULL,
    end_point GEOMETRY(Point, 4326) NOT NULL,
    geom GEOMETRY(LineString, 4326),
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_road_segments_geom ON road_segments USING GIST (geom);
CREATE INDEX idx_road_segments_status ON road_segments (current_status);
CREATE INDEX idx_road_segments_road ON road_segments (road_id);

CREATE TABLE IF NOT EXISTS bridges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    road_id UUID NOT NULL REFERENCES roads(id) ON DELETE CASCADE,
    segment_id UUID REFERENCES road_segments(id) ON DELETE SET NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    load_capacity_mt DOUBLE PRECISION DEFAULT 40.0,
    status VARCHAR(30) DEFAULT 'OPERATIONAL',
    structural_health_index DOUBLE PRECISION DEFAULT 95.0,
    last_inspection_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bridges_geom ON bridges USING GIST (location);
CREATE INDEX idx_bridges_status ON bridges (status);

CREATE TABLE IF NOT EXISTS infrastructure_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL, -- CHECKPOINT, FERRY_ROUTE, WAREHOUSE, HOSPITAL, RELIEF_CAMP, HELIPAD
    district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    capacity_desc VARCHAR(100),
    contact_phone VARCHAR(30),
    is_operational BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_infra_geom ON infrastructure_nodes USING GIST (location);
CREATE INDEX idx_infra_type ON infrastructure_nodes (type);

CREATE TABLE IF NOT EXISTS road_status_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    segment_id UUID NOT NULL REFERENCES road_segments(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    source VARCHAR(50) NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 0.95,
    start_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    reason TEXT,
    verified_by VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_road_status_segment ON road_status_events (segment_id, start_time DESC);

-- ----------------------------------------------------------------------------
-- 3. WEATHER OBSERVATIONS & AI RISK SCORES
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    district_id UUID REFERENCES districts(id),
    station_name VARCHAR(100),
    location GEOMETRY(Point, 4326) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    rainfall_mm DOUBLE PRECISION DEFAULT 0.0,
    temperature_c DOUBLE PRECISION DEFAULT 24.0,
    wind_kmh DOUBLE PRECISION DEFAULT 12.0,
    humidity_pct DOUBLE PRECISION DEFAULT 85.0,
    source VARCHAR(50) DEFAULT 'IMD_AWS'
);

CREATE INDEX idx_weather_obs_time ON weather_observations (timestamp DESC);
CREATE INDEX idx_weather_obs_geom ON weather_observations USING GIST (location);

CREATE TABLE IF NOT EXISTS risk_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    segment_id UUID NOT NULL REFERENCES road_segments(id) ON DELETE CASCADE,
    risk_type VARCHAR(50) NOT NULL,
    probability DOUBLE PRECISION NOT NULL,
    severity VARCHAR(20) NOT NULL,
    valid_from TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMPTZ NOT NULL,
    model_version VARCHAR(50) DEFAULT 'xgboost-ner-hazard-v2.4',
    confidence DOUBLE PRECISION DEFAULT 0.91,
    contributing_factors JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_scores_segment ON risk_scores (segment_id, valid_to);
CREATE INDEX idx_risk_scores_prob ON risk_scores (probability DESC);

-- ----------------------------------------------------------------------------
-- 4. INCIDENTS, HAZARDS & FIELD REPORTING
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL, -- landslide, flood, road_damage, bridge_closure, accident
    severity VARCHAR(30) NOT NULL DEFAULT 'HIGH',
    location_desc VARCHAR(200) NOT NULL,
    geom GEOMETRY(Point, 4326) NOT NULL,
    road_segment_id UUID REFERENCES road_segments(id) ON DELETE SET NULL,
    district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'REPORTED',
    reported_by UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    estimated_clearance_hours DOUBLE PRECISION DEFAULT 4.0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_incidents_geom ON incidents USING GIST (geom);
CREATE INDEX idx_incidents_status ON incidents (status);

CREATE TABLE IF NOT EXISTS field_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_uuid VARCHAR(64) UNIQUE NOT NULL, -- Idempotency key from mobile
    incident_id UUID REFERENCES incidents(id) ON DELETE SET NULL,
    reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    geom GEOMETRY(Point, 4326) NOT NULL,
    accuracy_m DOUBLE PRECISION DEFAULT 5.0,
    disruption_type VARCHAR(50) NOT NULL,
    severity VARCHAR(30) NOT NULL DEFAULT 'CRITICAL',
    description TEXT NOT NULL,
    media_files JSONB,
    offline_created_at TIMESTAMPTZ NOT NULL,
    synced_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    sync_status VARCHAR(30) DEFAULT 'SYNCED',
    device_id VARCHAR(100)
);

CREATE INDEX idx_field_reports_client_uuid ON field_reports (client_uuid);
CREATE INDEX idx_field_reports_geom ON field_reports USING GIST (geom);

-- ----------------------------------------------------------------------------
-- 5. FLEET, VEHICLES & HIGH-THROUGHPUT GPS TELEMETRY
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS drivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(120) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    blood_group VARCHAR(10) DEFAULT 'O+',
    status VARCHAR(30) DEFAULT 'AVAILABLE'
);

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number VARCHAR(30) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL, -- CRYO_TANKER, MULTI_AXLE_HEAVY, 4X4_TACTICAL_PICKUP
    capacity_mt DOUBLE PRECISION DEFAULT 15.0,
    owner VARCHAR(100) DEFAULT 'Govt of Assam Logistics',
    driver_id UUID REFERENCES drivers(id) ON DELETE SET NULL,
    current_status VARCHAR(30) DEFAULT 'ACTIVE',
    last_location GEOMETRY(Point, 4326),
    last_speed_kmh DOUBLE PRECISION DEFAULT 0.0,
    last_heading_deg DOUBLE PRECISION DEFAULT 0.0,
    cryo_temp_c DOUBLE PRECISION,
    last_ping_time TIMESTAMPTZ
);

CREATE INDEX idx_vehicles_reg ON vehicles (registration_number);
CREATE INDEX idx_vehicles_geom ON vehicles USING GIST (last_location);

-- GPS Telemetry Partitioned by Month for scale (5,000 updates/sec)
CREATE TABLE IF NOT EXISTS gps_readings (
    id BIGSERIAL,
    vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    speed_kmh DOUBLE PRECISION DEFAULT 0.0,
    heading_deg DOUBLE PRECISION DEFAULT 0.0,
    accuracy_m DOUBLE PRECISION DEFAULT 2.5,
    altitude_m DOUBLE PRECISION DEFAULT 250.0,
    ignition_status BOOLEAN DEFAULT TRUE,
    engine_temp_c DOUBLE PRECISION DEFAULT 85.0,
    cryo_temp_c DOUBLE PRECISION,
    navic_satellite_count INT DEFAULT 9,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE TABLE gps_readings_2026_10 PARTITION OF gps_readings
    FOR VALUES FROM ('2026-10-01 00:00:00+00') TO ('2026-11-01 00:00:00+00');

CREATE INDEX idx_gps_readings_veh_time ON gps_readings (vehicle_id, timestamp DESC);
CREATE INDEX idx_gps_readings_geom ON gps_readings USING GIST (location);

-- ----------------------------------------------------------------------------
-- 6. ALERTS & EMERGENCY DISASTER COORDINATION
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(30) NOT NULL DEFAULT 'HIGH',
    district_id UUID REFERENCES districts(id) ON DELETE SET NULL,
    road_id UUID REFERENCES roads(id) ON DELETE SET NULL,
    location_desc VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ
);

CREATE INDEX idx_alerts_status ON alerts (status);
CREATE INDEX idx_alerts_type ON alerts (type);

CREATE TABLE IF NOT EXISTS emergency_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(150) NOT NULL,
    type VARCHAR(50) DEFAULT 'MONSOON_SURGE',
    level VARCHAR(20) DEFAULT 'LEVEL_3',
    affected_districts JSONB NOT NULL,
    priority_corridors JSONB NOT NULL,
    activated_by UUID NOT NULL REFERENCES users(id),
    start_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_emergency_active ON emergency_events (is_active);
