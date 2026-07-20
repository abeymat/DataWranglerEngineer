# Product Spec

# Data Wrangler Engineer

Data Wrangler Engineer converts plain-English business data requirements into safe, tested, explainable, reusable Polars transformation workflows.

## Primary Demo Request

Create one row per customer. Combine all unique addresses into a readable address list, normalize U.S. phone numbers, calculate total purchases, retain the most recent transaction date, remove duplicates, flag records with missing customer IDs, and prepare the output for Salesforce import.

## Core User Flow

1. Upload a CSV dataset.
2. Receive a schema and quality profile.
3. Enter a natural-language business request.
4. Review a typed transformation plan.
5. Generate a constrained Polars workflow.
6. Execute the workflow in a controlled worker.
7. Run validation checks and show a test report.
8. Show a bounded repair attempt when a deterministic demo schema issue occurs.
9. Preview before-and-after data.
10. Save and rerun the workflow.
11. Export Salesforce-ready CSV output.

## Build Week Features

- CSV ingestion with file type, size, delimiter, encoding, null, duplicate, malformed-value, identifier, and type profiling.
- VLOOKUP-style two-CSV lookup preview using safe Polars left joins.
- Standalone browser workbench for CSV upload, profiling, planning, generation, and lookup preview.
- Pydantic workflow specification model.
- Operation graph that translates to Polars code.
- AST allowlist only as a secondary guard for generated code display or constrained snippets.
- Worker-process execution with timeout, sanitized errors, temporary directories, and cleanup.
- Validation suite for output columns, identifiers, row counts, totals, duplicates, date handling, and source immutability.
- Bounded repair loop with attempt history.
- SQLite workflow persistence for standalone demo.
- FastAPI v1 endpoints with typed request/response models and consistent error envelopes.
- Standalone enterprise-style web demo.
- Salesforce integration contract and retained Apex/LWC path.
- Build Week submission package and transparent Codex build log.

## Deferred Features

- Native Excel, JSON, API-response, and SOQL-result ingestion beyond extension-ready interfaces.
- Strong OS sandbox guarantees beyond documented worker isolation unless Docker worker is completed and verified.
- Multi-user production authentication.
- Full Salesforce managed package hardening.
- Large-file distributed execution.
- Automatic arbitrary workflow synthesis outside the approved operation set.
- Real customer-data classification beyond simple redaction heuristics.

## Success Criteria

- Main demo runs locally without a real OpenAI key by default.
- Real OpenAI integration is available behind configuration.
- Tests, linting, and type checks pass or documented exceptions are explicit.
- No committed secrets.
- Generated transformations are validated before presentation as successful.
- Failure and repair are deterministic for video recording.
