import pytest
import uuid
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_offline_field_report_sync():
    test_uuid = str(uuid.uuid4())
    sync_payload = {
        "device_id": "TEST-RUGGED-TAB",
        "sync_session_id": "SESSION-1234",
        "queue_items": [
            {
                "queue_id": "q-1",
                "client_uuid": test_uuid,
                "operation": "CREATE_FIELD_REPORT",
                "payload": {
                    "lat": 25.188,
                    "lon": 92.997,
                    "disruption_type": "Landslide",
                    "severity": "CRITICAL",
                    "description": "Culvert 14 washed out under heavy monsoon rain",
                    "media_files": []
                },
                "client_timestamp": datetime.now(timezone.utc).isoformat(),
                "device_id": "TEST-RUGGED-TAB"
            }
        ]
    }
    response = client.post("/api/v1/sync/queue", json=sync_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["processed_count"] == 1
    assert data["results"][0]["client_uuid"] == test_uuid
    assert data["results"][0]["status"] in ("SUCCESS", "CONFLICT_FLAGGED")

def test_offline_sync_idempotency():
    # Resending the exact same client_uuid should be skipped as DUPLICATE_SKIPPED
    fixed_uuid = "550e8400-e29b-41d4-a716-446655440000" # From seed data
    sync_payload = {
        "device_id": "TEST-RUGGED-TAB",
        "sync_session_id": "SESSION-1235",
        "queue_items": [
            {
                "queue_id": "q-dup",
                "client_uuid": fixed_uuid,
                "operation": "CREATE_FIELD_REPORT",
                "payload": {"lat": 25.188, "lon": 92.997, "disruption_type": "Landslide", "severity": "CRITICAL", "description": "Duplicate test"},
                "client_timestamp": datetime.now(timezone.utc).isoformat(),
                "device_id": "TEST-RUGGED-TAB"
            }
        ]
    }
    response = client.post("/api/v1/sync/queue", json=sync_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["results"][0]["status"] == "DUPLICATE_SKIPPED"

def test_delta_sync():
    response = client.get("/api/v1/sync/delta")
    assert response.status_code == 200
    data = response.json()
    assert "updated_roads" in data
    assert "active_incidents" in data
    assert "active_convoys" in data
