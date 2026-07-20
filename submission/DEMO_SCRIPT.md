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
7. Show the structured ETL plan with extract source and Salesforce Account load target.
8. Click `Generate Transform`.
9. Show the approved operation graph and generated Polars artifact.
10. Click `Run ETL`.
11. Show successful execution metrics, validation findings, transformed preview rows, and Salesforce load prep.
12. Highlight field mappings such as `customer_id` to `External_Id__c` and `customer_name` to `Name`.

## Codex And GPT-5.6 Callout

Codex accelerated the project as an engineering agent: it audited the starting repo, designed the ETL architecture, implemented FastAPI and Polars modules, built the UI, debugged runtime errors, added tests, and produced documentation.

The project is configured for GPT-5.6 with `OPENAI_MODEL=gpt-5.6-sol`. The deterministic demo path lets judges run the workflow without an API key, and the next phase wires GPT-5.6 into structured workflow planning and repair.

## Close

The result is a reusable, explainable Salesforce ETL workflow that is safer than spreadsheet-driven imports and more auditable than one-off scripts.
