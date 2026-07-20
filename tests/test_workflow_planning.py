from pathlib import Path

import polars as pl
from fastapi.testclient import TestClient

from app.ingestion.csv_profiler import profile_dataframe
from app.ingestion.models import DatasetProfile
from app.main import create_app
from app.planning.demo_planner import plan_workflow
from app.planning.models import WorkflowPlanRequest

DEMO_INSTRUCTION = (
    "Create one row per customer. Combine all unique addresses into a readable address list, "
    "normalize U.S. phone numbers, calculate total purchases, retain the most recent transaction "
    "date, remove duplicates, flag records with missing customer IDs, and prepare the output for "
    "Salesforce import."
)


def _demo_profile() -> DatasetProfile:
    path = Path("samples/customer_wrangling_demo.csv")
    dataframe = pl.read_csv(path, null_values=[""])
    return profile_dataframe(dataframe, path.name, ",", "utf-8")


def test_demo_planner_returns_structured_workflow_spec() -> None:
    response = plan_workflow(
        WorkflowPlanRequest(instruction=DEMO_INSTRUCTION, dataset_profile=_demo_profile())
    )

    spec = response.spec
    assert spec.workflow_name == "Customer Salesforce Import Wrangler"
    assert spec.grouping_keys == ["customer_id", "customer_name"]
    assert "total_purchases" in spec.output_columns
    assert len(spec.transformation_steps) == 7
    assert len(spec.validation_rules) >= 5
    assert any("duplicate" in warning.lower() for warning in spec.warnings)


def test_plan_endpoint_accepts_profile_payload() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/workflows/plan",
        json={
            "instruction": DEMO_INSTRUCTION,
            "dataset_profile": _demo_profile().model_dump(mode="json"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["spec"]["output_columns"][0] == "customer_id"
