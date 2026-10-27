from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_scan_endpoint(monkeypatch):
    monkeypatch.setattr("api.scan_infrastructure", lambda x: {"findings": []})
    response = client.post("/api/v1/scan", json={"file_path": "examples/vulnerable.json"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_simulate_endpoint(monkeypatch):
    monkeypatch.setattr("api.simulate_in_sandbox", lambda x, y: {"cost_savings": 50})
    response = client.post("/api/v1/simulate", json={
        "candidate_content": "{}", 
        "iac_format": "json"
    })
    assert response.status_code == 200

def test_remediate_endpoint(monkeypatch):
    monkeypatch.setattr("api.apply_remediation", lambda x, y: {"diff": "+ secure"})
    response = client.post("/api/v1/remediate", json={
        "file_path": "examples/vulnerable.json",
        "verified_content": "{}"
    })
    assert response.status_code == 200

def test_invalid_request():
    response = client.post("/api/v1/scan", json={})
    assert response.status_code == 422
