# Current State Audit

Reference project audited: `/Users/abeymathews/AntiGravityProjects/myDataAnalyticsVersion2`.

No files were modified in the reference project. This repository is the Build Week workspace for the transformed implementation.

## Repository Structure Observed

- `app.py`: monolithic FastAPI backend with upload, analysis, Salesforce OAuth/import, generated code execution, cleanup, and utility logic.
- `static/` and `templates/`: standalone web UI assets.
- `salesforce-app/`: Salesforce DX project with LWC, Apex controller, custom objects, named credential metadata, tabs, pages, and tests.
- `requirements.txt`, `runtime.txt`, `Procfile`, `.slugignore`: Python/Heroku deployment configuration.
- `sample_sales_data.csv`, `xy.csv`, `updatecontact.csv`: sample/input data.
- `test_*.py`: ad hoc Python tests and reproduction scripts.
- `README.md`, `README_MANAGED_PACKAGE.md`, `MIGRATION_TO_OPENAI.md`, `PROGRESS.md`, logs, Apex scripts, and helper scripts.
- `certs/`, `.env`, `.env.example`, logs, `uploads/`, and `results/`: local operational artifacts that need cleanup before public submission.

## Existing Reusable Components

- FastAPI routing and multipart upload foundation.
- Polars dependency and several Polars-oriented helpers, including CSV export handling for nested data.
- Initial AST allowlist concept for generated code.
- Session cleanup and startup/shutdown data wipe hooks.
- Salesforce Lightning Web Component with CSV upload, SOQL import, workflow save/run UI concepts, result preview, and loading states.
- Apex callout controller, Named Credential metadata, custom workflow objects, and Apex test class.
- Heroku deployment shape via `Procfile` and runtime files.
- Error-message mapping utility that can be evolved into structured error sanitization.

## Critical Problems And Risks

- Generated Python is executed with `exec` in the API process. The AST check is helpful but incomplete and does not provide OS-level isolation.
- Documentation claims Pandas/GPT-4 behavior while code has moved toward Polars and multiple AI providers.
- `.env.example` contains Salesforce-looking credentials and tokens. This must be replaced with placeholders before submission.
- Apex contains a hard-coded service token.
- CORS allows all origins.
- Logs appear to contain operational data and generated code. Logging policy must prevent secrets and full datasets.
- The backend is monolithic and mixes auth, Salesforce integration, profiling, generation, execution, and UI concerns.
- Uploaded data and result files are stored on disk by default in `uploads/` and `results/`.
- Tests are present but not organized as a dependable suite. `pytest` is not installed in the current workspace, so tests could not be run yet.
- OpenAI usage appears to rely on older chat-completions patterns in documentation and should be updated to current Responses API patterns after confirming SDK behavior.
- Salesforce UI is functional-looking but too broad for the Build Week demo path and includes duplicated state declarations.

## Current Run Commands

- Backend documented command: `python app.py` or `uvicorn app:app --reload`.
- Salesforce commands are driven from `salesforce-app/package.json`: `npm run lint`, `npm run test:unit`, `npm run prettier:verify`.
- Existing Python tests attempted with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/abeymathews/AntiGravityProjects/myDataAnalyticsVersion2 pytest -q -p no:cacheprovider /Users/abeymathews/AntiGravityProjects/myDataAnalyticsVersion2`.
- Result: failed before collection because `pytest` is not installed in the current environment.

## Preserve

- Salesforce project structure and integration contract ideas.
- FastAPI as backend framework.
- Polars as the transformation engine.
- CSV upload and result download flow.
- Existing workflow persistence concept in Salesforce custom objects, while adding local SQLite for standalone demo.
- Startup/shutdown cleanup intent.

## Replace Or Refactor

- In-process `exec` execution path.
- Free-form generated Pandas or broad Python code generation.
- Hard-coded credentials and service tokens.
- Global CORS and unauthenticated production APIs.
- Monolithic backend structure.
- Unversioned prompts and undocumented model configuration.

## Audit Conclusion

The existing project is a strong prototype with valuable Salesforce integration and a working FastAPI/UI base. For Build Week, it should be reshaped into a safer, explainable data-engineering workflow system: typed planning first, constrained Polars operation generation, isolated execution, validation, bounded repair, workflow persistence, and a polished deterministic demo.
