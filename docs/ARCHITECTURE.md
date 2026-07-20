# Architecture

## Target Shape

Salesforce ETL Engineer is a modular FastAPI application with a standalone web workbench. The product is organized around an ETL boundary:

- Extract source data into a temporary, profiled representation.
- Transform data through typed plans and approved Polars operation graphs.
- Load by producing a validated Salesforce import/upsert package and field mapping contract.

Direct Salesforce API writes are a future connector. The current load stage prepares Salesforce-ready CSV output and tells the operator what is ready, what is missing, and which Salesforce fields are expected.

## Backend Modules

- `app.core`: settings, logging, correlation IDs, error envelopes.
- `app.api`: FastAPI routers and typed request/response DTOs.
- `app.ingestion`: CSV validation, loading, schema profiling, and sample redaction.
- `app.lookup`: deterministic VLOOKUP-style joins for enriching source datasets.
- `app.planning`: natural-language requirement interpretation into `WorkflowSpec`.
- `app.operations`: approved operation graph and Polars code renderer.
- `app.execution`: controlled worker process, timeouts, stdout/error capture, and cleanup.
- `app.salesforce`: Salesforce load target models, field mapping contract, and load readiness checks.
- `app.static`: standalone browser ETL workbench served by FastAPI for local demos.

Planned modules:

- `app.validation`: broader validation rule catalog and generated test reports.
- `app.repair`: bounded repair orchestration with sanitized failure reports.
- `app.persistence`: SQLite repository and replaceable storage interface.
- `app.openai_client`: Responses API client, prompt loading, structured output validation, and mocks.

## Data Flow

1. `POST /api/v1/datasets/profile` accepts a CSV upload and returns a schema-quality profile.
2. `POST /api/v1/workflows/plan` creates a typed ETL plan from the profile and natural-language request.
3. `POST /api/v1/workflows/generate` creates an approved operation graph and rendered Polars code artifact.
4. `POST /api/v1/workflows/execute` runs the operation graph in a worker process.
5. Execution returns transformed preview rows, validation findings, reconciliation metrics, and a Salesforce load plan.
6. `POST /api/v1/salesforce/load-plan` can independently validate output columns against the Salesforce load contract.

## Security Boundaries

- Uploaded data is processed in memory or temporary objects and is not persisted by default.
- Saved workflows should store specifications, operation graphs, generated code artifacts, schema fingerprints, validation rules, model metadata, and execution history, not source datasets.
- Free-form model output is not trusted. It must validate against Pydantic models and approved operation schemas.
- Generated Polars code is displayed as an artifact of approved operations; the application executes the operation graph.
- Execution happens outside the main API process with a time limit and sanitized errors.
- Logs include correlation IDs, statuses, durations, and sanitized categories, never API keys, tokens, full datasets, or unredacted prompts.
- The current process worker is a reliability boundary, not a complete OS sandbox.

## API Surface

- `POST /api/v1/datasets/profile`
- `POST /api/v1/lookups/preview`
- `POST /api/v1/workflows/plan`
- `POST /api/v1/workflows/generate`
- `POST /api/v1/workflows/execute`
- `POST /api/v1/salesforce/load-plan`
- `GET /health`
- `GET /ready`
- `GET /`
- `GET /static/*`
- `GET /samples/*`

Planned API surface:

- `POST /api/v1/workflows/{id}/execute`
- `POST /api/v1/workflows/{id}/repair`
- `GET /api/v1/workflows/{id}`
- `GET /api/v1/workflows`
- `GET /api/v1/executions/{id}`

## Salesforce Load Contract

The default load target is Salesforce `Account` upsert with `External_Id__c` as the external ID field. The demo output maps:

- `customer_id` to `External_Id__c`
- `customer_name` to `Name`
- `address_list` to `ETL_Address_List__c`
- `normalized_phone` to `Phone`
- `total_purchases` to `Total_Purchases__c`
- `most_recent_transaction_date` to `Last_Transaction_Date__c`
- `missing_customer_id` to `Missing_Customer_Id__c`
- `salesforce_import_status` to `Data_Quality_Status__c`

Salesforce credentials, domains, tokens, and org IDs must never be hard-coded. Future direct-load integration should use Named Credentials, OAuth, protected custom metadata, and explicit operator approval before mutating Salesforce data.

## Execution Limitation

The first worker uses process isolation, strict operation allowlists, timeouts, and sanitized error handling. This is useful for deterministic local demos but is not equivalent to a hardened sandbox. A Docker-based worker or managed job runner should be implemented before handling untrusted arbitrary transforms in production.
