# Demo Script

Target length: under 3 minutes.

## Opening

This is Salesforce ETL Engineer, an AI-assisted ETL workbench for preparing safe Salesforce load packages from messy CSV data.

## Show The Problem

Salesforce imports are often prepared in spreadsheets or one-off scripts. That makes duplicate removal, address consolidation, phone normalization, external IDs, and validation hard to audit and rerun safely.

## Demo Flow

1. Open `http://127.0.0.1:8000/`.
2. Click `Load Sample`.
3. Click `Extract Profile`.
4. Show row count, columns, duplicates, warnings, and schema profile.
5. Click `Demo Request`.
6. Click `Plan Transform`.
7. Show `gpt-5.6-sol · medium reasoning`, the OpenAI response ID, the structured ETL plan, and the
   Salesforce Account load target.
8. Click `Generate Transform`.
9. Show the approved operation graph and generated Polars artifact.
10. Click `Run ETL`.
11. Show successful execution metrics, validation findings, transformed preview rows, and Salesforce load prep.
12. Highlight field mappings such as `customer_id` to `External_Id__c` and `customer_name` to `Name`.

## Codex And GPT-5.6 Callout

Codex accelerated the project as an engineering agent: it audited the starting repo, designed the ETL architecture, implemented FastAPI and Polars modules, built the UI, debugged runtime errors, added tests, and produced documentation.

GPT-5.6 Sol is the live planning engine in this recording. The Responses API receives the business
instruction and schema-quality metadata, returns strict structured output, and is prevented from
changing the executable operation graph. The response ID on screen demonstrates the live call.
The repository also includes a clearly labeled deterministic mode so judges can run the full ETL
flow without providing an API key.

Do not show an `approved local planner` result while narrating it as GPT-5.6. Before recording,
set `OPENAI_PLANNING_MODE=openai`, restart the server, and confirm the Plan tab names
`gpt-5.6-sol` and displays a response ID.

## Close

The result is a reusable, explainable Salesforce ETL workflow that is safer than spreadsheet-driven imports and more auditable than one-off scripts.
