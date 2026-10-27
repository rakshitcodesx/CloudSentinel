import os
import tempfile
from fastapi.testclient import TestClient
from api import app
from cloudsentinel.engine.repair import generate_and_verify_fix

client = TestClient(app)

def test_engine_generate_and_verify_fix(monkeypatch):
    # Mock LLM returning a valid fix
    monkeypatch.setattr("ollama.generate", lambda model, prompt: {"response": '{"Resource": "Secure"}'})
    # Mock the scanner verifying the fix (returning 0 findings)
    monkeypatch.setattr("cloudsentinel.engine.repair.scan_infrastructure", lambda path: {"findings": []})
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        temp_file.write(b'{"Resource": "Vulnerable"}')
        temp_path = temp_file.name
        
    try:
        result = generate_and_verify_fix(
            temp_path, 
            {"rule": "iam-no-admin", "description": "Admin access detected"}
        )
        assert result["success"] is True
        assert result["candidate_content"] == '{"Resource": "Secure"}'
    finally:
        os.remove(temp_path)

def test_api_auto_repair_endpoint(monkeypatch):
    # Mock the underlying engine function to skip file creation
    monkeypatch.setattr("api.generate_and_verify_fix", lambda path, finding, model: {
        "success": True, 
        "candidate_content": "{}"
    })
    
    response = client.post("/api/v1/auto-repair", json={
        "file_path": "examples/vulnerable.json",
        "rule_id": "iam-no-admin",
        "description": "Admin access detected"
    })
    
    assert response.status_code == 200
    assert response.json()["data"]["success"] is True
