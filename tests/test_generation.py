from pathlib import Path

import polars as pl
from fastapi.testclient import TestClient

from app.ingestion.csv_profiler import profile_dataframe
from app.main import create_app
from app.operations.generator import generate_workflow
from app.operations.models import OperationType, WorkflowGenerateRequest
from app.planning.demo_planner import plan_workflow
from app.planning.models import WorkflowPlanRequest, WorkflowSpec


def _demo_spec() -> WorkflowSpec:
    path = Path("samples/customer_wrangling_demo.csv")
    dataframe = pl.read_csv(path, null_values=[""])
    profile = profile_dataframe(dataframe, path.name, ",", "utf-8")
    plan = plan_workflow(
        WorkflowPlanRequest(
            instruction="Prepare the customer dataset for Salesforce import.",
            dataset_profile=profile,
        )
    )
    return plan.spec


def test_generate_workflow_returns_approved_operation_graph_and_polars_code() -> None:
    response = generate_workflow(WorkflowGenerateRequest(spec=_demo_spec()))

    operation_types = {
        operation.operation_type for operation in response.operation_graph.operations
    }
    assert OperationType.GROUP_CUSTOMERS in operation_types
    assert "import polars as pl" in response.polars_code
    assert "import pandas" not in response.polars_code
    assert "exec(" not in response.polars_code
    assert "input_df.clone()" in response.polars_code


def test_generate_endpoint_returns_code_and_graph() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/workflows/generate",
        json={"spec": _demo_spec().model_dump(mode="json")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["operation_graph"]["graph_id"] == "customer_salesforce_import_v1"
    assert "def transform" in body["polars_code"]
