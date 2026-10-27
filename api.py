from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server import scan_infrastructure, simulate_in_sandbox, apply_remediation

app = FastAPI(
    title="CloudSentinel API",
    description="DevSecOps CI/CD guardrail API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    file_path: str

class SimulateRequest(BaseModel):
    candidate_content: str
    iac_format: str

class RemediateRequest(BaseModel):
    file_path: str
    verified_content: str

@app.post("/api/v1/scan")
def scan_endpoint(request: ScanRequest):
    try:
        result = scan_infrastructure(request.file_path)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulate")
def simulate_endpoint(request: SimulateRequest):
    try:
        result = simulate_in_sandbox(request.candidate_content, request.iac_format)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/remediate")
def remediate_endpoint(request: RemediateRequest):
    try:
        result = apply_remediation(request.file_path, request.verified_content)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from cloudsentinel.engine.repair import generate_and_verify_fix

class AutoRepairRequest(BaseModel):
    file_path: str
    rule_id: str
    description: str
    model: str = "codellama"

@app.post("/api/v1/auto-repair")
def auto_repair_endpoint(request: AutoRepairRequest):
    finding = {"rule": request.rule_id, "description": request.description}
    result = generate_and_verify_fix(request.file_path, finding, request.model)
    
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
        
    return {"status": "success", "data": result}

from cloudsentinel.formatters.sarif import generate_sarif
from cloudsentinel.integrations.github import post_pr_comment

class SarifRequest(BaseModel):
    findings: list
    file_path: str = "infrastructure.json"

class GithubCommentRequest(BaseModel):
    repo: str
    pr_number: int
    comment_body: str

@app.post("/api/v1/export/sarif")
def export_sarif_endpoint(request: SarifRequest):
    try:
        sarif_data = generate_sarif(request.findings, request.file_path)
        return {"status": "success", "data": sarif_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/github/pr-comment")
def github_pr_comment_endpoint(request: GithubCommentRequest):
    try:
        result = post_pr_comment(request.repo, request.pr_number, request.comment_body)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


