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
OPENAI_PLANNING_MODE=openai
OPENAI_REASONING_EFFORT=medium
```

This appears in:

- `.env.example`
- `app/core/settings.py`
- `app/openai_client/workflow_planner.py`
- `prompts/workflow_planner_v1.md`

## Implemented GPT-5.6 Path

When an API key is configured, `Plan Transform` calls GPT-5.6 Sol through the Responses API and
parses the result directly into a strict Pydantic model. The request uses explicit `medium`
reasoning, low text verbosity, `store=false`, a timeout, and bounded transient retries.

GPT-5.6 contributes:

- Business-readable interpretation of the natural-language Salesforce outcome.
- Step and validation explanations tailored to the profiled schema.
- Explicit assumptions and data-quality warnings.
- Structured output that the application can validate rather than scraping model prose.

The host application retains control of required columns, operation order and parameters,
Salesforce field mappings, validation severity, and execution. Only schema-quality metadata is
sent; filenames, samples, preview rows, complete source data, and credentials are excluded.

## Judge And Demo Modes

- `OPENAI_PLANNING_MODE=openai` proves the live GPT-5.6 path and fails clearly if it is unavailable.
- `OPENAI_PLANNING_MODE=auto` uses GPT-5.6 when configured and visibly labels the approved local
  fallback otherwise.
- `OPENAI_PLANNING_MODE=deterministic` provides a fully local judge path.

The Plan tab displays the actual provider, effective model, reasoning effort, and response ID. The
test suite mocks all API calls, so tests never need or spend a real key.

## Why Other GPT-5.6 Features Are Not Enabled

Pro mode, persisted reasoning, Programmatic Tool Calling, explicit caching, and multi-agent beta
were reviewed but intentionally excluded. This path is one bounded structured planning request
with no model tools or multi-turn state. Adding those features without an evaluation would increase
cost and complexity without improving the approved ETL execution boundary.

## Transparency Statement

Do not claim that transformation execution or every local run uses GPT-5.6. The accurate statement is:

GPT-5.6 Sol is implemented for structured ETL planning when API access is configured. The model
does not execute code or receive the full dataset. The approved operation graph and Polars worker
perform transformation and validation. A clearly labeled local planner keeps the project testable
without judge credentials.
