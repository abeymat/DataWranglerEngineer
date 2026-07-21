# Salesforce ETL Engineer

Salesforce ETL Engineer is a local FastAPI and Polars workbench for preparing safe Salesforce load packages from CSV data. It extracts and profiles source files, uses GPT-5.6 Sol or an approved local fallback to turn a plain-English outcome into a typed ETL plan, generates an approved Polars operation graph, executes it in a controlled worker, validates the result, and produces a Salesforce Account upsert load plan.

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

The no-key path is ready immediately. To demonstrate live GPT-5.6 Sol planning, create `.env`
from `.env.example`, set `OPENAI_API_KEY`, and use:

```env
OPENAI_MODEL=gpt-5.6-sol
OPENAI_PLANNING_MODE=openai
OPENAI_REASONING_EFFORT=medium
```

Restart Uvicorn after changing `.env`. `auto` uses GPT-5.6 when a key is present and visibly
falls back to the approved local planner when it is not. The Plan tab identifies the actual
planner and displays the OpenAI response ID for a live call.

## Demo Flow

1. Click `Load Sample`.
2. Click `Extract Profile`.
3. Click `Demo Request`.
4. Click `Plan Transform`.
5. Click `Generate Transform`.
6. Click `Run ETL`.
7. Review the Salesforce load prep tab for field mappings and readiness.

## Build Week Submission Notes

- Suggested category: developer tool or business/productivity tool, depending on the final submission form options.
- Repository URL: `https://github.com/abeymat/DataWranglerEngineer`
- Submission support files live in `submission/`.
- The demo video should be under 3 minutes and show the app working end to end.
- The narration should explicitly cover where Codex accelerated engineering work and show a GPT-5.6 Sol structured planning result.
- Get the Codex session ID with `/feedback` from the Codex session where the core functionality was built, then paste that ID into the submission form.

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

The OpenAI path uses the official Python SDK and Responses API structured outputs with
`gpt-5.6-sol`, explicit `medium` reasoning, low response verbosity, a 45-second timeout, and at
most two SDK retries for transient errors. It sends the business instruction and schema-quality
metadata only; filenames, preview rows, and sample values are excluded. Model output is validated
with Pydantic and mapped onto the approved operation sequence before generation. See
[`docs/OPENAI_INTEGRATION.md`](docs/OPENAI_INTEGRATION.md) for modes and limitations.

## Current Limitations

- CSV is the only implemented extractor.
- Salesforce loading currently means validated CSV package preparation, not direct API writes.
- Workflow persistence and repair orchestration are planned next phases.
- The worker process is not a hardened OS sandbox.
- GPT-5.6 access and API billing depend on the operator's OpenAI project; automated tests use mocks.
