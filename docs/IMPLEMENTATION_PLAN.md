# Implementation Plan

## Phase 1: Salesforce ETL Pivot

- Rename the product surface to Salesforce ETL Engineer.
- Add explicit extract source and Salesforce load target metadata to workflow planning.
- Add a Salesforce load contract that validates required output columns and maps source columns to Salesforce fields.
- Update docs, tests, and UI copy to reflect ETL rather than generic data wrangling.

## Phase 2: Extract Foundation

- Keep CSV as the first extraction source.
- Preserve file type, size, delimiter, encoding, malformed row, null, duplicate, identifier, and type profiling.
- Add extension interfaces for Excel, JSON, SOQL query results, and API payloads.

## Phase 3: Transform Foundation

- Use `gpt-5.6-sol` through Responses API structured outputs for schema-only requirement
  interpretation, with an explicit `medium` reasoning baseline and approved local fallback.
- Continue using typed `WorkflowSpec` and approved operation graphs.
- Keep Polars as the only transformation engine.
- Expand the operation catalog for common Salesforce ETL tasks: picklists, external IDs, owner assignment, reference lookups, date/time normalization, and multi-object splits.

## Phase 4: Load Foundation

- Keep Salesforce-ready CSV as the current load output.
- Add object-specific load contracts for `Account`, `Contact`, `Lead`, and custom objects.
- Add configurable field mapping profiles.
- Add downloadable CSV export and load manifest.
- Defer direct Salesforce writes until security and approval controls are implemented.

## Phase 5: Controlled Execution And Validation

- Keep execution outside the main API process.
- Add richer validation rules for Salesforce required fields, external IDs, duplicate keys, picklist values, phone/email formats, and referential lookups.
- Preserve reconciliation metrics and before/after previews.

## Phase 6: Repair Loop

- Add bounded repair attempts, failure classification, sanitized reports, and deterministic demo repair path.
- Never allow uncontrolled autonomous retries.

## Phase 7: Workflow Persistence

- Add SQLite repository and workflow history model.
- Persist ETL definitions, versions, load targets, field mappings, validation rules, and execution summaries.
- Do not persist source datasets by default.

## Phase 8: Salesforce UI And Integration

- Keep the standalone browser workbench as the primary demo surface.
- Add Apex/LWC DTOs only after the backend contract stabilizes.
- Use Named Credentials or protected metadata for backend endpoint and authentication.
- Include mocks and tests for any Salesforce metadata added.

## Phase 9: UX Refinement

- Polish the ETL timeline, source profile, transform plan, operation graph, validation findings, load plan, and output preview.
- Add clear empty, loading, success, warning, and failure states.
- Keep the UI restrained and enterprise-focused.

## Phase 10: Full Testing And Security Review

- Expand tests for schema profiling, operation graphs, load contracts, output validation, error sanitization, repair limits, and API integration.
- Run pytest, ruff, mypy, and a secrets review before completing each major phase.

## Phase 11: Deployment And Reproducibility

- Finalize README, `.env.example`, Dockerfile, setup commands, test commands, production start command, and troubleshooting.
- Keep the backend runnable locally without Salesforce access.

## Phase 12: Submission Materials

- Update Build Week submission materials around Salesforce ETL: problem, architecture, Codex contribution, safety design, demo script, known limitations, and roadmap.

## Current Implementation Slice

1. Product renamed to Salesforce ETL Engineer.
2. Workflow plan includes extract source and Salesforce load target.
3. Execution response includes Salesforce load readiness and field mappings.
4. UI presents an ETL timeline and Salesforce load prep panel.
5. GPT-5.6 Sol structured planning is implemented with model provenance, safe context reduction,
   response validation, policy reconciliation, transient retry configuration, and a no-key path.
6. Tests cover load contracts, deterministic and mocked GPT planning, privacy boundaries,
   fallback behavior, execution responses, and UI copy without requiring a real API key.
