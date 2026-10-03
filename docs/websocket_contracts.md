# NER-LogiSense: WebSocket & SSE Event Contract Specification

## 1. Overview
Real-time operational awareness in NER-LogiSense is achieved through persistent, low-overhead WebSocket and Server-Sent Event (SSE) streams.
These channels deliver:
1. High-frequency vehicle GPS telemetry, speed, heading, and cryogenic temperature readouts.
2. Mission-critical disaster alerts, blockades, and automated diversion broadcasts.

---

## 2. Endpoints & Channels

| Protocol | Path | Channel | Primary Consumers |
| :--- | :--- | :--- | :--- |
| **WebSocket** | `/ws/telemetry` | `telemetry` | Dispatchers, Fleet Tracking HUD, Cryo Cold-chain Ops |
| **WebSocket** | `/ws/alerts` | `alerts` | State Disaster Control Rooms, District Magistrates, Field Units |
| **SSE** | `/api/v1/events/stream` | Multi-stream | Low-bandwidth mobile web views |

### Connection Handshake
Clients connect to the gateway with an optional JWT token parameter:
```text
wss://api.ner-logisense.gov.in/ws/telemetry?token=eyJhbGciOi...
```

---

## 3. Telemetry Event Payloads

### 3.1. Standard Vehicle Telemetry (`TELEMETRY_UPDATE`)
Broadcast when an active convoy updates location.
```json
{
  "event": "TELEMETRY_UPDATE",
  "vehicle_id": "8a7c2b51-9f12-4e89-b0f3-5e921d7b1029",
  "registration_number": "AS-01-GB-4091",
  "lat": 25.7502,
  "lon": 93.1674,
  "speed_kmh": 42.5,
  "heading_deg": 138.0,
  "altitude_m": 420.0,
  "navic_satellite_count": 9,
  "cryo_temp_c": -22.4,
  "anomalies": []
}
```

### 3.2. Cryogenic Cold-Chain Breach (`CRYO_TEMPERATURE_BREACH`)
Broadcast with high urgency when vaccine or oxygen temperature rises above threshold.
```json
{
  "event": "CRYO_TEMPERATURE_BREACH",
  "vehicle_id": "8a7c2b51-9f12-4e89-b0f3-5e921d7b1029",
  "registration_number": "AS-01-GB-4091",
  "severity": "CRITICAL",
  "title": "Cryo Temperature Alert: AS-01-GB-4091",
  "message": "Cryogenic temperature climbed to -8.5°C (Safe limit: -15.0°C). Cold-chain integrity compromised!",
  "current_temp_c": -8.5,
  "threshold_temp_c": -15.0,
  "cargo_type": "MEDICAL_OXYGEN",
  "timestamp": "2026-10-03T14:45:00Z"
}
```

---

## 4. Tactical Alert & Emergency Payloads

### 4.1. Road Blockade / Hazard Alert (`TACTICAL_ALERT`)
Broadcast when a road section is rendered impassable.
```json
{
  "event": "TACTICAL_ALERT",
  "alert_id": "a901f421-2e11-47a8-89c1-778899aabbcc",
  "type": "LANDSLIDE_BLOCKADE",
  "severity": "CRITICAL",
  "priority": "DEFCON_1_CRITICAL",
  "location": "NH-27 KM 141.8 Barail Escarpment (Near Bridge #4)",
  "message": "CRITICAL: 80m landslide severed NH-27. Jatinga Bypass diversion activated for relief convoys.",
  "district": "Dima Hasao (Haflong)",
  "affected_highway": "NH-27",
  "suggested_action": "REROUTE_VIA_JATINGA_BYPASS"
}
```

### 4.2. Emergency Disaster Mode Activated (`EMERGENCY_MODE_ACTIVATED`)
Triggered when State Disaster Management activates catastrophic storm protocol.
```json
{
  "event": "EMERGENCY_MODE_ACTIVATED",
  "title": "Active Monsoon Surge Protocol (Level-3)",
  "level": "LEVEL_3",
  "affected_districts": [
    "Dima Hasao (Haflong)",
    "East Khasi Hills (Shillong)",
    "Cachar (Silchar)",
    "Champhai"
  ],
  "priority_corridors": ["NH-27", "NH-6", "NH-102"],
  "activated_at": "2026-10-03T14:40:00Z"
}
```

---

## 5. Keepalive & Reconnection Protocol
- **Ping/Pong Heartbeat:** Gateway sends a heartbeat frame every 30 seconds:
  `{"type": "PING"}`
  Client responds with:
  `{"type": "PONG"}`
- **Auto-Reconnect with Exponential Backoff:** Clients must reconnect with exponential jitter ($1\text{s}, 2\text{s}, 4\text{s}, 8\text{s}$, capped at $30\text{s}$) to avoid thundering herd during connectivity recovery in mountain sectors.
