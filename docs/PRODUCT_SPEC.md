# Product Spec

# Salesforce ETL Engineer

Salesforce ETL Engineer is an AI-assisted ETL workbench for preparing trustworthy Salesforce loads from business-owned datasets. It extracts and profiles source data, converts a plain-English Salesforce outcome into a typed transformation plan, executes an approved Polars operation graph, validates the result, and produces a Salesforce-ready load package.

The current implementation supports CSV extraction and Salesforce-ready CSV load preparation. Direct writes to Salesforce are intentionally deferred until OAuth, Named Credential, Bulk API behavior, retry policy, and operator approvals are implemented and tested.

## Primary Demo Request

Create one row per customer. Combine all unique addresses into a readable address list, normalize U.S. phone numbers, calculate total purchases, retain the most recent transaction date, remove duplicates, flag records with missing customer IDs, and prepare the output for Salesforce Account upsert.

## Core ETL User Flow

1. Extract a CSV source dataset.
2. Receive schema, type, duplicate, null, malformed value, and identifier profiling.
3. Enter a natural-language Salesforce load objective.
4. Review a typed ETL plan with extract source, transform steps, validation rules, and Salesforce load target.
5. Generate an approved Polars operation graph and readable Polars code artifact.
6. Execute the transform in a controlled worker process.
7. Run validation and reconciliation checks.
8. Preview before-and-after data.
9. Review the Salesforce load plan, field mappings, required columns, and readiness status.
10. Export or hand off the Salesforce-ready CSV load package.
11. Save and rerun the workflow when persistence is enabled.

## Build Week Features

- CSV extraction with file type, size, delimiter, encoding, null, duplicate, malformed-value, identifier, and type profiling.
- VLOOKUP-style two-CSV lookup preview for enriching load sources before transformation.
- Standalone browser ETL workbench for upload, profiling, planning, generation, execution, validation, and load preparation.
- Pydantic `WorkflowSpec` with extract source and Salesforce load target metadata.
- Approved operation graph that translates to Polars code instead of executing arbitrary generated Python.
- Worker-process execution with timeout, sanitized errors, and no default source-data persistence.
- Validation suite for output columns, identifiers, row counts, totals, duplicates, date handling, and Salesforce load readiness.
- Salesforce load contract for Account upsert CSVs, including source-to-target field mappings and missing-column reporting.
- FastAPI v1 endpoints with typed request/response models and consistent error envelopes.
- Health and readiness endpoints for local and container deployments.

## Deferred Features

- Direct Salesforce writes through Bulk API, Composite API, or Apex callouts.
- Native Excel, JSON, API-response, and SOQL-result extraction beyond extension-ready boundaries.
- Strong OS sandbox guarantees beyond documented worker isolation unless a Docker worker is completed and verified.
- Multi-user production authentication and role-based approval workflows.
- Full Salesforce managed package hardening.
- Large-file distributed execution.
- Automatic arbitrary workflow synthesis outside the approved operation set.
- Real customer-data classification beyond simple profiling and redaction heuristics.

## Success Criteria

- Main ETL demo runs locally without a real OpenAI key by default.
- Salesforce load prep is explicit, validated, and not confused with direct org writes.
- Tests, linting, and type checks pass or documented exceptions are explicit.
- No committed secrets or real customer data.
- Uploaded source data is not persisted unexpectedly.
- Generated transformations are validated before being presented as successful.
