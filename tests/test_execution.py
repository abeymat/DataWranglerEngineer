from pathlib import Path

import polars as pl
from fastapi.testclient import TestClient

from app.execution.transformations import execute_operation_graph
from app.ingestion.csv_profiler import profile_dataframe
from app.main import create_app
from app.operations.generator import generate_workflow
from app.operations.models import OperationGraph, WorkflowGenerateRequest
from app.planning.demo_planner import plan_workflow
from app.planning.models import WorkflowPlanRequest


def _demo_graph() -> OperationGraph:
    path = Path("samples/customer_wrangling_demo.csv")
    dataframe = pl.read_csv(path, null_values=[""])
    profile = profile_dataframe(dataframe, path.name, ",", "utf-8")
    plan = plan_workflow(
        WorkflowPlanRequest(
            instruction="Prepare the customer dataset for Salesforce import.",
            dataset_profile=profile,
        )
    )
    generated = generate_workflow(WorkflowGenerateRequest(spec=plan.spec))
    return generated.operation_graph


def test_execute_operation_graph_transforms_customer_dataset() -> None:
    dataframe = pl.read_csv(Path("samples/customer_wrangling_demo.csv"), null_values=[""])

    result = execute_operation_graph(dataframe, _demo_graph())

    assert result.metrics.input_row_count == 8
    assert result.metrics.duplicate_rows_removed == 1
    assert result.metrics.output_row_count == 5
    assert result.metrics.missing_customer_id_count == 1
    assert result.metrics.invalid_phone_count == 1
    assert result.metrics.source_purchase_total == result.metrics.output_purchase_total
    assert "salesforce_import_status" in result.output_df.columns
    assert result.output_df.filter(pl.col("customer_id").is_null()).height == 1


def test_execute_endpoint_returns_preview_and_validation() -> None:
    client = TestClient(create_app())
    graph = _demo_graph()

    with Path("samples/customer_wrangling_demo.csv").open("rb") as file:
        response = client.post(
            "/api/v1/workflows/execute",
            files={"file": ("customer_wrangling_demo.csv", file, "text/csv")},
            data={"operation_graph": graph.model_dump_json()},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["execution_status"] == "passed"
    assert body["metrics"]["input_row_count"] == 8
    assert body["metrics"]["output_row_count"] == 5
    assert len(body["preview_rows"]) == 5
    assert any(finding["rule_id"] == "exec_val_004" for finding in body["validation_findings"])
