import json
import multiprocessing as mp
import time
from typing import Any

import polars as pl
from fastapi import UploadFile
from pydantic import ValidationError

from app.core.errors import AppError
from app.execution.models import ExecutionMetrics, WorkflowExecuteResponse
from app.execution.transformations import execute_operation_graph
from app.execution.validator import validate_execution
from app.ingestion.csv_loader import load_csv_upload
from app.operations.models import OperationGraph

EXECUTION_TIMEOUT_SECONDS = 10
PREVIEW_LIMIT = 25


class WorkerResult:
    def __init__(self, output_df: pl.DataFrame, metrics: ExecutionMetrics) -> None:
        self.output_df = output_df
        self.metrics = metrics


async def execute_workflow_upload(
    file: UploadFile,
    operation_graph_raw: str,
    max_upload_bytes: int,
) -> WorkflowExecuteResponse:
    loaded = await load_csv_upload(file, max_upload_bytes=max_upload_bytes)
    graph = _parse_operation_graph(operation_graph_raw)
    start = time.perf_counter()
    result = _run_worker(loaded.dataframe, graph)
    duration_ms = int((time.perf_counter() - start) * 1000)

    findings = validate_execution(result.metrics, result.output_df.columns)
    warnings = [
        finding.message
        for finding in findings
        if finding.status in {"warning", "failed"}
    ]

    return WorkflowExecuteResponse(
        execution_status="passed" if not any(f.status == "failed" for f in findings) else "failed",
        graph_id=graph.graph_id,
        input_dataset=loaded.filename,
        output_columns=result.output_df.columns,
        metrics=result.metrics,
        validation_findings=findings,
        warnings=warnings,
        preview_rows=result.output_df.head(PREVIEW_LIMIT).to_dicts(),
        duration_ms=duration_ms,
    )


def _parse_operation_graph(raw: str) -> OperationGraph:
    try:
        payload = json.loads(raw)
        return OperationGraph.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise AppError("Operation graph JSON is invalid.", "invalid_operation_graph", 400) from exc


def _run_worker(dataframe: pl.DataFrame, graph: OperationGraph) -> WorkerResult:
    queue: mp.Queue[dict[str, Any]] = mp.Queue(maxsize=1)
    process = mp.Process(
        target=_worker_entrypoint,
        args=(dataframe, graph.model_dump(mode="json"), queue),
    )
    process.start()
    process.join(EXECUTION_TIMEOUT_SECONDS)
    if process.is_alive():
        process.terminate()
        process.join(2)
        raise AppError("Workflow execution timed out.", "execution_timeout", 408)
    if queue.empty():
        raise AppError(
            "Workflow execution failed without a structured result.",
            "execution_failed",
            500,
        )
    payload = queue.get()
    if not payload.get("success"):
        raise AppError(
            "Workflow execution failed: " + str(payload.get("error", "unknown error")),
            "execution_failed",
            400,
        )
    output_df = pl.DataFrame(payload["output_rows"])
    metrics = ExecutionMetrics.model_validate(payload["metrics"])
    return WorkerResult(
        output_df=output_df,
        metrics=metrics,
    )


def _worker_entrypoint(
    dataframe: pl.DataFrame,
    graph_payload: dict[str, Any],
    queue: mp.Queue[dict[str, Any]],
) -> None:
    try:
        graph = OperationGraph.model_validate(graph_payload)
        result = execute_operation_graph(dataframe, graph)
        queue.put(
            {
                "success": True,
                "output_rows": result.output_df.to_dicts(),
                "metrics": result.metrics.model_dump(mode="json"),
            }
        )
    except Exception as exc:
        queue.put({"success": False, "error": _sanitize_error(exc)})


def _sanitize_error(exc: Exception) -> str:
    message = str(exc).strip()
    if not message:
        return exc.__class__.__name__
    return message[:240]
