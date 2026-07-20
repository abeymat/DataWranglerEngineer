# Architecture

## Target Shape

Data Wrangler Engineer is a modular FastAPI application with a standalone web UI and a Salesforce integration contract.

## Backend Modules

- `app.core`: settings, logging, correlation IDs, error envelopes.
- `app.api`: FastAPI routers and typed request/response DTOs.
- `app.ingestion`: CSV validation, loading, schema profiling, and sample redaction.
- `app.lookup`: deterministic VLOOKUP-style joins for appending fields from a lookup dataset.
- `app.planning`: natural-language requirement interpretation into `WorkflowSpec`.
- `app.operations`: approved transformation operation graph and Polars code renderer.
- `app.execution`: controlled worker process, timeouts, stdout/error capture, cleanup.
- `app.validation`: validation rules, reconciliation metrics, and test report generation.
- `app.repair`: bounded repair orchestration with sanitized failure reports.
- `app.persistence`: SQLite repository and replaceable storage interface.
- `app.openai_client`: Responses API client, prompt loading, structured output validation, mocks.
- `app.salesforce`: output contract and Salesforce-ready CSV helpers.
- `app.static`: standalone browser workbench served by FastAPI for local demos.

## Security Boundaries

- Uploaded data is processed in temporary storage and not persisted by default.
- Saved workflows store specifications, operation graphs, generated code, schema fingerprints, validation rules, model metadata, and execution history, not source datasets.
- Generated workflow execution happens outside the main API process.
- Free-form model output is never trusted. It must validate against Pydantic models and approved operation schemas.
- If code text is generated, AST checks enforce import, call, attribute, and name restrictions before worker execution.
- Logs include correlation IDs, status, durations, and sanitized categories, never API keys, tokens, full datasets, or unredacted prompts.

## API Surface

- `POST /api/v1/datasets/profile`
- `POST /api/v1/lookups/preview`
- `POST /api/v1/workflows/plan`
- `POST /api/v1/workflows/generate`
- `POST /api/v1/workflows/{id}/execute`
- `POST /api/v1/workflows/{id}/repair`
- `GET /api/v1/workflows/{id}`
- `GET /api/v1/workflows`
- `GET /api/v1/executions/{id}`
- `GET /health`
- `GET /ready`
- `GET /`
- `GET /static/*`
- `GET /samples/*`

## Salesforce Contract

Salesforce should call the same backend capability through stable DTOs. Apex must not hard-code tokens. Named Credentials or protected custom metadata should provide endpoint and auth configuration. LWC should show upload, profile, plan, execution status, validation findings, result preview, download, save, and rerun states.

## Execution Limitation

The first safe worker uses process isolation, strict operation allowlists, timeouts, temporary directories, and sanitized error handling. This is not equivalent to a complete OS sandbox. Docker-based worker isolation is preferred when practical and should be documented separately when implemented.
