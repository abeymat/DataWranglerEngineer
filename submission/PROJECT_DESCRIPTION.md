# Project Description

## Project Name

Salesforce ETL Engineer

## Category

Suggested category: developer tool or business/productivity tool, depending on the available Build Week submission categories.

## What It Does

Salesforce ETL Engineer is a local FastAPI and Polars application that prepares safe Salesforce load packages from CSV data. A user uploads or loads a source CSV, profiles the data, describes the Salesforce outcome in plain English, reviews a structured ETL plan, generates an approved Polars operation graph, executes the transform, validates the result, and reviews a Salesforce Account upsert load plan.

The current demo prepares Salesforce-ready CSV output and a field mapping contract. It does not directly write into a Salesforce org.

## Problem

Business teams often need to clean and reshape customer data before loading it into Salesforce. Spreadsheet formulas and one-off scripts are fragile, hard to audit, and easy to rerun incorrectly. Direct imports can create duplicate Accounts, malformed phone numbers, bad totals, and missing external IDs.

## Solution

The project turns the data-load process into an explainable ETL workflow:

- Extract CSV source data and profile schema/quality.
- Transform data using a typed plan and approved Polars operation graph.
- Load by preparing a validated Salesforce-ready CSV contract and field mappings.

## Technical Architecture

- FastAPI backend with typed Pydantic request/response models.
- Polars for profiling and transformation.
- Controlled worker process for ETL execution.
- Salesforce load contract module for Account upsert readiness.
- Standalone browser UI served by the same backend.
- Synthetic sample datasets for deterministic judging/demo.

## How Codex Helped

Codex was used as an engineering agent to audit the repository, reshape the product direction, design the architecture, implement the FastAPI/Polars modules, build the UI, debug runtime errors, add tests, update documentation, and produce submission materials.

## How GPT-5.6 Is Used

The repo is configured for GPT-5.6 via `OPENAI_MODEL=gpt-5.6-sol`. The current reliable demo path uses deterministic local planning/generation so judges can run it without an API key. The next OpenAI-backed phase will use GPT-5.6 for structured requirement interpretation and workflow planning once API access is available for the running environment.

## Safety Design

- Uploaded data is not persisted by default.
- The app executes approved operation graphs, not arbitrary model-generated Python.
- Worker execution is outside the main API process.
- Errors are sanitized and surfaced with correlation IDs.
- Salesforce credentials are not hard-coded.
- Direct Salesforce writes are deferred until OAuth, approval, retry, and rollback controls are implemented.

## What Was Built During Build Week

- Salesforce ETL product pivot.
- CSV profiling and quality reporting.
- Structured workflow planning model.
- Approved Polars operation graph generation.
- Controlled ETL execution and validation.
- Salesforce Account upsert load contract.
- Standalone enterprise-style web workbench.
- Tests, docs, README, and submission support materials.

## What Existed Before Build Week

The original reference project had a broader data analytics/Salesforce prototype shape. This Build Week workspace preserved useful ideas like FastAPI, CSV workflows, Salesforce-oriented output, and UI concepts while restructuring the project into a safer ETL architecture.

## Future Roadmap

- GPT-5.6-backed structured planning and repair loop.
- Workflow persistence and rerun history.
- Downloadable CSV export package.
- Additional Salesforce object contracts such as Contact, Lead, and custom objects.
- Direct Salesforce load connector with Named Credentials/OAuth and explicit operator approval.
- Docker worker isolation for stronger execution boundaries.
