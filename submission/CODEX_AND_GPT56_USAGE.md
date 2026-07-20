# Codex And GPT-5.6 Usage

## Codex Contributions

Codex was used throughout the project as an engineering agent, not only as code completion.

Key contributions:

- Repository audit and product pivot from generic data wrangling to Salesforce ETL.
- Architecture documentation and `AGENTS.md`.
- FastAPI module structure and typed API endpoints.
- CSV profiling and synthetic sample data flow.
- Workflow planning and approved operation graph design.
- Polars transformation execution and validation.
- Salesforce load contract and field mapping model.
- Standalone UI build and repeated browser debugging.
- Test suite creation and maintenance.
- README and Build Week submission materials.

## GPT-5.6 Configuration

The project default OpenAI model is configured as:

```env
OPENAI_MODEL=gpt-5.6-sol
```

This appears in:

- `.env.example`
- `app/core/settings.py`

## Current Demo Behavior

The main local demo path does not require an OpenAI API key. It uses deterministic local planning/generation so judges can run the workflow reliably.

This is intentional for the submission demo:

- It avoids requiring judge API credentials.
- It keeps the video path deterministic.
- It makes the safety boundary clear.

## Planned GPT-5.6 Path

GPT-5.6 will be used for:

- Natural-language requirement interpretation.
- Structured ETL plan generation.
- Validation rule suggestions.
- Bounded repair recommendations when execution or validation fails.

All model responses must be validated with Pydantic and translated into approved operation graphs before execution.

## Transparency Statement

Do not claim that the current demo sends every request to GPT-5.6. The accurate statement is:

The project is configured for GPT-5.6 and designed for GPT-5.6-backed planning, while the current reliable judging demo uses deterministic local planning/generation to avoid API-key dependency.
