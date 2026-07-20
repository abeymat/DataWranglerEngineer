# Salesforce ETL Engineer

Salesforce ETL Engineer is a local FastAPI and Polars workbench for preparing safe Salesforce load packages from CSV data. It extracts and profiles source files, turns a plain-English Salesforce outcome into a typed ETL plan, generates an approved Polars operation graph, executes it in a controlled worker, validates the result, and produces a Salesforce Account upsert load plan.

Direct Salesforce writes are not enabled in the current demo. The app prepares Salesforce-ready CSV output and a field mapping contract.

## Quick Start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Demo Flow

1. Click `Load Sample`.
2. Click `Extract Profile`.
3. Click `Demo Request`.
4. Click `Plan Transform`.
5. Click `Generate Transform`.
6. Click `Run ETL`.
7. Review the Salesforce load prep tab for field mappings and readiness.

## Main API Endpoints

- `POST /api/v1/datasets/profile`
- `POST /api/v1/lookups/preview`
- `POST /api/v1/workflows/plan`
- `POST /api/v1/workflows/generate`
- `POST /api/v1/workflows/execute`
- `POST /api/v1/salesforce/load-plan`
- `GET /health`
- `GET /ready`

## Checks

```bash
pytest
ruff check .
mypy app tests
```

## Environment

Copy `.env.example` to `.env` for local overrides. Do not commit real Salesforce credentials, API keys, tokens, org IDs, or customer data.

## Current Limitations

- CSV is the only implemented extractor.
- Salesforce loading currently means validated CSV package preparation, not direct API writes.
- Workflow persistence and repair orchestration are planned next phases.
- The worker process is not a hardened OS sandbox.
