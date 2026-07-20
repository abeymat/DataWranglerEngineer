from fastapi.testclient import TestClient

from app.main import create_app
from app.salesforce.load_contract import build_salesforce_load_plan


def test_salesforce_load_plan_maps_demo_columns_to_account_fields() -> None:
    plan = build_salesforce_load_plan(
        [
            "customer_id",
            "customer_name",
            "address_list",
            "normalized_phone",
            "total_purchases",
            "most_recent_transaction_date",
            "missing_customer_id",
            "salesforce_import_status",
        ]
    )

    mapping = {item.source_column: item.target_field for item in plan.field_mappings}
    assert plan.ready_for_load is True
    assert plan.target.object_api_name == "Account"
    assert mapping["customer_id"] == "External_Id__c"
    assert mapping["customer_name"] == "Name"
    assert mapping["normalized_phone"] == "Phone"


def test_salesforce_load_plan_endpoint_reports_missing_required_columns() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/salesforce/load-plan",
        json={"output_columns": ["customer_id", "customer_name"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["load_plan"]["ready_for_load"] is False
    assert body["load_plan"]["missing_output_columns"] == ["salesforce_import_status"]
