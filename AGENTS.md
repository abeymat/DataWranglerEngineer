# AGENTS.md

## Product Purpose

Salesforce ETL Engineer is an AI-assisted ETL application for preparing safe, tested, explainable Salesforce load packages from business datasets. The app extracts source data, transforms it through approved Polars operation graphs, validates the result, and prepares Salesforce-ready CSV output with field mappings and load-readiness checks.

## Repository Structure

- `app/`: FastAPI backend and core product logic.
- `app/api/`: HTTP routers and request/response DTOs.
- `app/ingestion/`: source loading and schema profiling. CSV is the first supported extractor.
- `app/lookup/`: deterministic VLOOKUP-style source enrichment.
- `app/planning/`: typed ETL specifications and model-assisted planning boundaries.
- `app/operations/`: approved operation graph and Polars rendering.
- `app/execution/`: controlled worker execution and transformation results.
- `app/salesforce/`: Salesforce load target models, field mappings, and load readiness checks.
- `app/static/`: standalone ETL workbench served by FastAPI.
- `prompts/`: versioned prompt templates when OpenAI planning is added.
- `samples/`: synthetic demo datasets only.
- `tests/`: pytest suite.
- `docs/`: architecture, audit, product, implementation, and Salesforce contract documentation.
- `submission/`: Build Week submission materials when present.

## Architectural Boundaries

- API handlers orchestrate services; they should not contain transformation logic.
- Extractors load and profile data but must not silently discard invalid rows.
- Planning produces typed ETL specs, not executable code.
- Operation graphs are the preferred executable representation.
- Generated code, when present, is an artifact rendered from approved operations or strictly validated text.
- Execution must happen outside the main API process.
- Salesforce loading currently means validated load-package preparation, not direct org mutation.
- Persistence stores workflow definitions and metadata, not uploaded source datasets by default.

## Coding Conventions

- Use Python 3.12+.
- Use FastAPI, Pydantic, Polars, pytest, ruff, and mypy where configured.
- Prefer small typed functions and explicit exception classes.
- Keep prompts in `prompts/`.
- Keep sample data synthetic and clearly labeled.
- Do not add broad frameworks without documenting why.

## Commands

- Setup: `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`
- Development: `uvicorn app.main:app --reload`
- Tests: `pytest`
- Coverage: `pytest --cov=app --cov-report=term-missing`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy app tests`

Update this section if tooling changes.

## Security Requirements

- Never commit secrets, tokens, private keys, real credentials, or real customer data.
- Never log full uploaded datasets, API keys, auth tokens, or unredacted prompts containing customer data.
- Uploaded data must be temporary unless explicit configuration enables retention.
- Use correlation IDs for request logs.
- CORS must be environment-specific.
- Salesforce credentials and service tokens must come from Named Credentials, protected metadata, or environment configuration, not source code.
- Direct Salesforce writes require explicit design, operator approval, retry policy, test coverage, and rollback guidance before implementation.

## Generated Polars Code Validation

- Prefer approved operation graphs translated into Polars.
- Generated code must not use pandas, arbitrary imports, `eval`, `exec`, network access, environment variables, subprocesses, or unrestricted filesystem access.
- Validate model responses with Pydantic before execution.
- If code text is accepted, parse with AST and enforce allowlisted nodes, names, calls, attributes, and imports.
- Execute outside the main API process with timeouts and temporary directories.
- Run validation and Salesforce load-readiness checks before marking an ETL run successful.

## Files Not To Modify Without Strong Reason

- `samples/` data semantics for the primary demo.
- `prompts/` templates without updating prompt version notes.
- Salesforce load contracts without updating tests and docs.
- Migration and architecture docs without recording the reason.
- Salesforce metadata that affects existing org deployment unless corresponding Apex/LWC tests are updated.

## Required Checks Before Completing A Task

- Run relevant tests.
- Run linting and type checking when configured.
- Confirm no secrets were added.
- Confirm uploaded data is not persisted unexpectedly.
- Confirm generated transformations are validated.
- Confirm Salesforce load readiness is surfaced honestly.
- Update docs for architectural or security changes.
- Record unresolved risks in the final response.

## Architectural Decisions

Document meaningful decisions in `docs/ARCHITECTURE.md` or a future `docs/decisions/ADR-YYYYMMDD-title.md`. Include context, decision, consequences, and alternatives considered.
