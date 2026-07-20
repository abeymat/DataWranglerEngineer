# Current State Audit

## Scope

This repository is the Build Week workspace for Salesforce ETL Engineer. The original reference project in `/Users/abeymathews/AntiGravityProjects/myDataAnalyticsVersion2` was not modified.

## Current Product Shape

The application is now positioned as a Salesforce-focused ETL tool:

- Extract: CSV upload, validation, delimiter detection, encoding handling, Polars loading, and schema/quality profiling.
- Transform: natural-language request to typed `WorkflowSpec`, approved operation graph generation, and Polars code rendering.
- Load: Salesforce-ready CSV preparation with Account upsert field mappings and load-readiness checks.

The current load stage does not write directly to Salesforce. It prepares and validates the package that an operator or future connector can load.

## Repository Structure

- `app/main.py`: FastAPI app factory, health/readiness routes, static UI, samples, and API routers.
- `app/api/`: dataset, lookup, workflow, and Salesforce load-plan endpoints.
- `app/ingestion/`: CSV loading and profiling.
- `app/planning/`: ETL planning models and deterministic demo planner.
- `app/operations/`: approved operation graph models, generator, and Polars renderer.
- `app/execution/`: worker-process execution, result models, transformation logic, and validation.
- `app/salesforce/`: Salesforce load target, field mapping, and readiness contract.
- `app/static/`: standalone browser ETL workbench.
- `samples/`: synthetic demo CSVs.
- `tests/`: pytest suite.
- `docs/`: audit, product, architecture, implementation, and Salesforce contract documentation.

## Reusable Components Preserved

- FastAPI app structure and typed routers.
- Polars-based CSV profiling and transformation path.
- Deterministic customer-to-Salesforce demo scenario.
- VLOOKUP-style two-CSV lookup preview.
- Controlled process-based execution layer.
- Validation findings and reconciliation metrics.
- Synthetic sample datasets.
- Standalone UI served by the backend.

## Current Known Gaps

- Direct Salesforce writes are not implemented and should not be implied.
- Workflow persistence is documented but not yet implemented.
- Repair loop is planned but not yet implemented in the main path.
- OpenAI Responses API integration is planned but currently represented by deterministic local planning/generation.
- Execution worker is not a hardened operating-system sandbox.
- CSV export/download button is still needed for a complete load handoff.
- Salesforce Apex/LWC metadata for this revised ETL contract is not yet implemented in this workspace.

## Security And Reliability Findings

- Uploaded source data is processed for requests and is not persisted by default.
- The application executes an approved operation graph, not arbitrary model-generated Python.
- Errors are sanitized before returning from worker execution.
- No credentials or Salesforce org identifiers are required for the current local demo.
- `.env.example` uses placeholders and should remain secret-free.
- Direct Salesforce mutation requires a separate security design with Named Credentials, OAuth, approvals, retry policy, audit logging, and tests.

## How The Application Currently Runs

Local setup:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the UI at `http://127.0.0.1:8000/` and the API docs at `http://127.0.0.1:8000/docs`.

Checks:

```bash
pytest
ruff check .
mypy app tests
```

## Audit Conclusion

The project has a solid FastAPI/Polars foundation and a reliable local demo path. The Salesforce ETL pivot should continue incrementally: first strengthen load-package export and object-specific contracts, then add persistence, repair, and finally direct Salesforce integration only after safety and approval controls exist.
