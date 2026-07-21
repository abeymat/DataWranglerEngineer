# GPT-5.6 Sol Integration

## Purpose

GPT-5.6 Sol interprets the natural-language Salesforce objective and returns a strict structured
planning result. The application then reconciles that result with its approved customer Account
ETL contract. The model never supplies executable Python and cannot directly change Salesforce.

## API Contract

- SDK: official `openai` Python package, pinned in `requirements.txt`.
- Endpoint: Responses API through `client.responses.parse`.
- Model: `gpt-5.6-sol`.
- Reasoning: explicit `medium`, preserving the previous GPT-5.5 baseline.
- Output: Pydantic `ModelWorkflowPlan` structured output.
- Storage flag: `store=false`.
- Text verbosity: `low`.
- Timeout: 45 seconds by default.
- Retries: at most two SDK retries for transient API/network failures.

GPT-5.6 Sol is the flagship tier and the `gpt-5.6` alias routes to it. This project uses the
explicit Sol identifier so logs and submission evidence are unambiguous. See the official
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model) and
[GPT-5.6 Sol model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol).

## Data Minimization

The model request contains:

- The user's business instruction.
- Column names and inferred types.
- Null, uniqueness, duplicate, malformed-row, and identifier metadata.
- Schema and Salesforce load-contract metadata.

The request excludes source filenames, column sample values, preview rows, complete datasets,
credentials, and Salesforce tokens. `store=false` is set on the request, but the project does not
claim Zero Data Retention or a complete data-classification system.

## Trust Boundary

The strict model DTO allows business descriptions, assumptions, and warnings. A policy layer
requires the exact approved step and validation-rule sequence, preserves the original user
instruction, and supplies operation parameters, columns, validation severity, and Salesforce
mappings from application-owned templates. The next stage generates an allowlisted operation
graph; model text is never passed to `eval` or `exec`.

## Planning Modes

- `auto`: use GPT-5.6 Sol when `OPENAI_API_KEY` is configured; otherwise use and label the approved
  local planner. Sanitized OpenAI failures also produce a visibly marked local fallback.
- `openai`: require GPT-5.6 Sol. Missing credentials or rejected output returns a consistent error
  envelope instead of falling back.
- `deterministic`: always use the approved local planner.

For the recorded Build Week demo, use `OPENAI_PLANNING_MODE=openai` so a visible
`gpt-5.6-sol` planner label and OpenAI response ID prove the live path. Judges without credentials
can use `auto` or `deterministic` and run the remainder of the ETL flow locally.

## Deliberately Unused GPT-5.6 Features

Pro mode, persisted reasoning, Programmatic Tool Calling, explicit prompt caching, and the
multi-agent beta are not enabled. The planner is one bounded structured-output request with no
tools and no multi-turn model state. These features should be added only after an evaluation shows
a quality, latency, or cost benefit for a concrete workflow.

## Verification

Automated tests mock the Responses resource and verify the model ID, reasoning effort,
`store=false`, structured-output type, privacy-reduced payload, policy rejection, token metadata,
fallback categories, and required-key behavior. Tests do not require or spend a real API key.
