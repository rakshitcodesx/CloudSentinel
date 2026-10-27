# CloudSentinel Architecture Context

## Current State
CloudSentinel is a zero-trust infrastructure-as-code guardrail and automated CI/CD pipeline. 

## Tech Stack
* **Backend:** Python, FastAPI, FastMCP, pytest
* **Engine:** AWS Cedar (policy evaluation), Moto (in-memory AWS simulation)
* **AI Integration:** Ollama (local LLM repair loop via Codellama)
* **CI/CD:** SARIF export, GitHub REST API pull request integration
* **Frontend:** Next.js 15, React, Tailwind CSS

## Project Structure
* `api.py`: FastAPI REST layer
* `server.py`: FastMCP tools interface
* `cloudsentinel/engine/`: Core logic (`evaluator.py`, `sandbox.py`, `repair.py`)
* `cloudsentinel/formatters/`: Output generation (`sarif.py`)
* `cloudsentinel/integrations/`: Third-party webhooks (`github.py`)
* `cloudsentinel/policies/`: `.cedar` zero-trust rules
* `frontend/`: Next.js web dashboard
* `tests/`: Pytest suite (18 passing tests, >70% coverage)
