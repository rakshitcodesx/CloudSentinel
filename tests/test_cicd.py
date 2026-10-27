import os
import pytest
from fastapi.testclient import TestClient
from api import app
from cloudsentinel.formatters.sarif import generate_sarif
from cloudsentinel.integrations.github import post_pr_comment
import httpx

client = TestClient(app)

def test_generate_sarif():
    findings = [{"rule": "iam-no-admin", "description": "Admin detected"}]
    sarif = generate_sarif(findings, "template.yaml")
    
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"][0]["results"]) == 1
    assert sarif["runs"][0]["results"][0]["ruleId"] == "iam-no-admin"
    assert sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "template.yaml"

def test_github_post_comment(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake_token")
    
    # Mock httpx.post to return a successful response
    class MockResponse:
        def raise_for_status(self): pass
        def json(self): return {"html_url": "https://github.com/fake/comment"}
        
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: MockResponse())
    
    result = post_pr_comment("rakshitcodesx/cloudsentinel", 1, "Fix applied!")
    assert result["status"] == "success"
    assert result["comment_url"] == "https://github.com/fake/comment"

def test_github_missing_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is missing"):
        post_pr_comment("repo", 1, "body")

def test_api_sarif_endpoint():
    response = client.post("/api/v1/export/sarif", json={
        "findings": [{"rule": "s3-public", "description": "Public S3 bucket"}],
        "file_path": "s3.json"
    })
    assert response.status_code == 200
    assert response.json()["data"]["version"] == "2.1.0"

def test_api_github_endpoint(monkeypatch):
    monkeypatch.setattr("api.post_pr_comment", lambda repo, pr, body: {"status": "success", "comment_url": "url"})
    response = client.post("/api/v1/github/pr-comment", json={
        "repo": "rakshitcodesx/cloudsentinel",
        "pr_number": 1,
        "comment_body": "Vulnerabilities found!"
    })
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "success"
