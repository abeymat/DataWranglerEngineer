# AGENTS.md

## Product Purpose

Data Wrangler Engineer is an AI-powered data-engineering app that turns plain-English business requirements into safe, tested, explainable, reusable Polars transformation workflows.

## Repository Structure

- `app/`: FastAPI backend and core product logic.
- `app/api/`: HTTP routers and request/response DTOs.
- `app/ingestion/`: dataset loading and schema profiling.
- `app/planning/`: typed workflow specifications and model-assisted planning.
- `app/operations/`: approved operation graph and Polars rendering.
- `app/execution/`: controlled worker execution.
- `app/validation/`: output rules and reconciliation checks.
- `app/repair/`: bounded repair loop.
- `app/persistence/`: workflow repository.
- `app/salesforce/`: Salesforce integration contract.
- `prompts/`: versioned prompt templates.
- `samples/`: synthetic demo datasets only.
- `tests/`: pytest suite.
- `docs/`: architecture, audit, product, and implementation documentation.
- `submission/`: Build Week submission materials.

## Architectural Boundaries

- API handlers orchestrate services; they should not contain transformation logic.
- Ingestion profiles data but must not silently discard invalid rows.
- Planning produces typed specs, not executable code.
- Operation graphs are the preferred executable representation.
- Generated code, when present, is an artifact rendered from approved operations or strictly validated text.
- Execution must happen outside the main API process.
- Persistence stores workflow definitions and metadata, not uploaded source datasets by default.

## Coding Conventions

- Use Python 3.12+.
- Use FastAPI, Pydantic, Polars, pytest, ruff, and mypy/pyright where configured.
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

## Generated Polars Code Validation

- Prefer approved operation graphs translated into Polars.
- Generated code must not use pandas, arbitrary imports, `eval`, `exec`, network access, environment variables, subprocesses, or unrestricted filesystem access.
- Validate model responses with Pydantic before execution.
- If code text is accepted, parse with AST and enforce allowlisted nodes, names, calls, attributes, and imports.
- Execute outside the main API process with timeouts and temporary directories.
- Run validation rules before marking a workflow successful.

## Files Not To Modify Without Strong Reason

- `samples/` data semantics for the primary demo.
- `prompts/` templates without updating prompt version notes.
- Migration and architecture docs without recording the reason.
- Salesforce metadata that affects existing org deployment unless corresponding Apex/LWC tests are updated.

## Required Checks Before Completing A Task

- Run relevant tests.
- Run linting and type checking when configured.
- Confirm no secrets were added.
- Confirm uploaded data is not persisted unexpectedly.
- Confirm generated transformations are validated.
- Update docs for architectural or security changes.
- Record unresolved risks in the final response.

## Architectural Decisions

Document meaningful decisions in `docs/ARCHITECTURE.md` or a future `docs/decisions/ADR-YYYYMMDD-title.md`. Include context, decision, consequences, and alternatives considered.
