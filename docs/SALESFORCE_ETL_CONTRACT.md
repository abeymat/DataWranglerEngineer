# Salesforce ETL Contract

## Current Load Mode

The current load mode is `csv_package`: the backend prepares transformed rows, validation findings, reconciliation metrics, and a Salesforce field mapping plan. It does not perform direct Salesforce API writes.

This keeps the demo safe and honest while preserving a clean path toward Data Loader, Bulk API, or Apex/LWC integration.

## Default Target

- System: Salesforce
- Object: `Account`
- Operation: `upsert`
- External ID field: `External_Id__c`
- Output format: CSV

## Required Output Columns

- `customer_id`
- `customer_name`
- `salesforce_import_status`

Rows missing required output columns are not considered ready for load. Rows with missing customer IDs are preserved and flagged so the operator can decide whether to repair or exclude them before import.

## Default Field Mapping

- `customer_id` -> `External_Id__c`
- `customer_name` -> `Name`
- `address_list` -> `ETL_Address_List__c`
- `normalized_phone` -> `Phone`
- `total_purchases` -> `Total_Purchases__c`
- `most_recent_transaction_date` -> `Last_Transaction_Date__c`
- `missing_customer_id` -> `Missing_Customer_Id__c`
- `salesforce_import_status` -> `Data_Quality_Status__c`

## API

Create or validate a load plan:

```http
POST /api/v1/salesforce/load-plan
Content-Type: application/json
```

```json
{
  "output_columns": [
    "customer_id",
    "customer_name",
    "address_list",
    "normalized_phone",
    "total_purchases",
    "most_recent_transaction_date",
    "missing_customer_id",
    "salesforce_import_status"
  ]
}
```

Workflow execution also returns `salesforce_load_plan` so the UI can show whether the transformed output is ready for Salesforce loading.

## Future Direct Load Requirements

Before implementing direct Salesforce writes:

- Use OAuth and Named Credentials or protected metadata.
- Require explicit user approval before mutating Salesforce data.
- Support dry-run validation.
- Validate required fields, external IDs, duplicate external IDs, picklists, references, and field-level access.
- Use Bulk API or Composite API with documented retry behavior.
- Store only workflow metadata and execution summaries unless source-data retention is explicitly enabled.
- Add Apex mocks, Apex tests, LWC error/loading states, and backend integration tests.
- Document rollback and partial-failure handling.
