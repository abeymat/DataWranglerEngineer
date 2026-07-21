# Build Week Submission Checklist

Use this checklist against the OpenAI Build Week submission page.

## Required Form Items

- Category selected.
- Project description pasted into the submission form.
- Public YouTube demo video under 3 minutes.
- Code repository URL added: `https://github.com/abeymat/DataWranglerEngineer`
- Repository is public, or private and shared with `testing@devpost.com` and `build-week-event@openai.com`.
- Codex `/feedback` session ID from the session where most core functionality was built.

## Repository Requirements

- `README.md` includes setup instructions.
- `README.md` includes sample data and demo flow.
- `README.md` includes clear guidance for running and testing the project.
- `samples/` contains synthetic demo CSVs.
- No secrets, API keys, Salesforce tokens, private certs, or real customer data are committed.
- Tests can be run locally with `pytest`.
- Linting can be run locally with `ruff check .`.
- Type checking can be run locally with `mypy app tests`.

## Codex And GPT-5.6 Evidence

- Demo narration explains how Codex accelerated repository audit, architecture, implementation, debugging, tests, and docs.
- Recorded demo runs with `OPENAI_PLANNING_MODE=openai` and visibly shows `gpt-5.6-sol` plus an
  OpenAI response ID.
- Demo narration explains that GPT-5.6 performs structured schema-only planning while the approved
  operation graph and worker perform transformation.
- Submission description is transparent about the no-key local fallback and does not present it as
  a model call.
- Mocked tests verify the GPT-5.6 request contract without requiring a real API key.
- `submission/CODEX_AND_GPT56_USAGE.md` is up to date.

## Demo Video Must Show

- App running locally at `http://127.0.0.1:8000/`.
- Load sample CSV.
- Extract/profile source data.
- Show structured ETL plan.
- Show GPT-5.6 Sol model provenance and response ID.
- Show generated operation graph or Polars code.
- Run ETL successfully.
- Show Salesforce load prep, field mappings, validation, and output preview.
- Mention current limitation: current load stage prepares Salesforce-ready CSV/load contract, not direct Salesforce writes.

## Optional Developer Tool Notes

If submitted as a developer tool, include:

- Installation instructions.
- Supported platform: local Python/FastAPI app on macOS/Linux/Windows with Python and pip.
- A way for judges to test without rebuilding from scratch: sample CSVs and deterministic local demo flow.
