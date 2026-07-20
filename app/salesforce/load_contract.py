from app.salesforce.models import SalesforceFieldMapping, SalesforceLoadPlan, SalesforceLoadTarget

DEFAULT_ACCOUNT_REQUIRED_COLUMNS = ["customer_id", "customer_name", "salesforce_import_status"]

DEFAULT_ACCOUNT_FIELD_MAP = {
    "customer_id": "External_Id__c",
    "customer_name": "Name",
    "address_list": "ETL_Address_List__c",
    "normalized_phone": "Phone",
    "total_purchases": "Total_Purchases__c",
    "most_recent_transaction_date": "Last_Transaction_Date__c",
    "missing_customer_id": "Missing_Customer_Id__c",
    "salesforce_import_status": "Data_Quality_Status__c",
}


def build_salesforce_load_plan(
    output_columns: list[str],
    target: SalesforceLoadTarget | None = None,
) -> SalesforceLoadPlan:
    load_target = target or SalesforceLoadTarget()
    available = set(output_columns)
    required_columns = _required_columns_for_target(load_target)
    missing = [column for column in required_columns if column not in available]

    mappings = [
        SalesforceFieldMapping(
            source_column=column,
            target_field=DEFAULT_ACCOUNT_FIELD_MAP[column],
            required=column in required_columns,
        )
        for column in output_columns
        if column in DEFAULT_ACCOUNT_FIELD_MAP
    ]

    notes = [
        "Current load stage prepares a Salesforce-ready CSV contract; "
        "direct API writes are deferred.",
        "Load rows with Salesforce Data Import Wizard, Data Loader, Bulk API, "
        "or Apex/LWC integration.",
    ]
    if load_target.operation == "upsert":
        notes.append(
            f"Upsert requires {load_target.external_id_field} to be configured in Salesforce."
        )
    if missing:
        notes.append("Missing required output columns must be repaired before loading.")

    return SalesforceLoadPlan(
        target=load_target,
        field_mappings=mappings,
        required_output_columns=required_columns,
        missing_output_columns=missing,
        ready_for_load=not missing,
        notes=notes,
    )


def _required_columns_for_target(target: SalesforceLoadTarget) -> list[str]:
    if target.object_api_name == "Account":
        return DEFAULT_ACCOUNT_REQUIRED_COLUMNS
    return ["customer_id"]
