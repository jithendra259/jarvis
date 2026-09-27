import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "JARVIS"
    assert data["status"] == "online"

def test_api_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "hardware" in data
    assert "cpu_count_logical" in data["hardware"]
    assert "ram_total_gb" in data["hardware"]
    assert "os" in data["hardware"]

def test_api_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["port"] == 8000
    assert "database_path" in data
