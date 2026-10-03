import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "NER-LogiSense" in data["service"]

def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ner-logisense.gov.in", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["role"] == "Super Admin"

def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ner-logisense.gov.in", "password": "WrongPassword!"}
    )
    assert response.status_code == 401

def test_otp_flow():
    req = client.post("/api/v1/auth/otp/request", json={"phone": "+919864012345"})
    assert req.status_code == 200
    
    verify = client.post("/api/v1/auth/otp/verify", json={"phone": "+919864012345", "otp": "704820"})
    assert verify.status_code == 200
    assert "access_token" in verify.json()
