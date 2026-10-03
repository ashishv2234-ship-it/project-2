import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_roads():
    response = client.get("/api/v1/network/roads")
    assert response.status_code == 200
    roads = response.json()
    assert len(roads) > 0
    codes = [r["code"] for r in roads]
    assert "NH-27" in codes

def test_accessibility_summary():
    response = client.get("/api/v1/network/accessibility-summary")
    assert response.status_code == 200
    data = response.json()
    assert "operational_pct" in data
    assert "total_network_km" in data
    assert data["active_blockades_count"] >= 0

def test_plan_route():
    response = client.post(
        "/api/v1/routes/plan",
        json={
            "origin_name": "Guwahati Central Depot",
            "origin_lat": 26.182,
            "origin_lon": 91.758,
            "destination_name": "Haflong / Silchar Relief Camp",
            "dest_lat": 25.188,
            "dest_lon": 92.997,
            "optimization_priority": "SAFEST"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_direct_route_available"] is True
    assert len(data["routes"]) >= 1
    # Check Route A is recommended
    route_a = data["routes"][0]
    assert route_a["option_tag"] == "A"
    assert "Jatinga" in route_a["route_name"] or "NH-27" in route_a["route_name"]
    assert route_a["is_recommended"] is True

def test_emergency_corridors():
    response = client.get("/api/v1/routes/emergency-corridors")
    assert response.status_code == 200
    corrs = response.json()
    assert len(corrs) >= 2
