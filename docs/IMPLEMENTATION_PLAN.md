# Implementation Plan

## Phase 1: Audit And Product Specification

- Create repository-level audit, product spec, architecture, implementation plan, and `AGENTS.md`.
- Record existing test/lint status and security risks.

## Phase 2: Architecture And Security Foundation

- Scaffold Python package structure, settings, error envelopes, logging, and health endpoints.
- Add `.env.example`, README baseline, Docker skeleton, and test tooling.

## Phase 3: Dataset Profiling

- Implement CSV validation, delimiter detection, encoding handling, Polars loading, schema profiling, and sample datasets.
- Add unit tests.

## Phase 4: Structured Workflow Planning

- Define Pydantic workflow spec and deterministic demo planner.
- Add OpenAI Responses API adapter with mocked tests.

## Phase 5: Safe Transformation Generation

- Implement approved operation graph and Polars renderer.
- Add allowlist tests and generated-code readability checks.

## Phase 6: Controlled Execution And Validation

- Execute operation graph in a worker process with timeout and temp cleanup.
- Add validation rules, reconciliation metrics, and API integration tests.

## Phase 7: Repair Loop

- Add bounded repair attempts, failure classification, sanitized reports, and deterministic demo repair path.

## Phase 8: Workflow Persistence

- Add SQLite repository and workflow history model.
- Persist workflows without source data.

## Phase 9: Salesforce And Standalone UI Integration

- Build standalone demo UI.
- Improve Salesforce DTOs, Apex callout contract, mocks, tests, loading, errors, and setup docs.

## Phase 10: UX Refinement

- Polish layout, accessibility, responsive behavior, data previews, timeline, validation, and export flow.

## Phase 11: Full Testing And Security Review

- Expand tests, run lint/type checks, review logs and secrets, verify failure paths.

## Phase 12: Deployment And Reproducibility

- Finalize Dockerfile, lock files, setup commands, production start, and troubleshooting.

## Phase 13: Submission Materials

- Create Devpost draft, demo script, shot list, technical summary, judging map, limitations, architecture diagram, and Codex build log.

## Phase 14: Demo Rehearsal And Release Audit

- Run end-to-end happy path, repair path, save/rerun/export flow, and final release checklist.

## First Implementation Slice

1. Scaffold backend package and tests.
2. Implement settings, logging, error envelopes, health/readiness.
3. Implement CSV profiler and sample datasets.
4. Add deterministic workflow spec for the primary demo.
5. Add tests that do not require OpenAI credentials.
