from typing import Annotated

from fastapi import APIRouter, File, Form, Request, UploadFile

from app.core.logging import app_logger
from app.core.settings import get_settings
from app.execution.models import WorkflowExecuteResponse
from app.execution.service import execute_workflow_upload
from app.operations.generator import generate_workflow
from app.operations.models import WorkflowGenerateRequest, WorkflowGenerateResponse
from app.planning.models import WorkflowPlanRequest, WorkflowPlanResponse
from app.planning.service import plan_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/plan", response_model=WorkflowPlanResponse)
def create_workflow_plan(
    payload: WorkflowPlanRequest,
    request: Request,
) -> WorkflowPlanResponse:
    response = plan_workflow(payload)
    app_logger.info(
        "workflow_plan_completed provider=%s model=%s duration_ms=%s fallback=%s "
        "fallback_category=%s",
        response.planning.provider,
        response.planning.effective_model,
        response.planning.duration_ms,
        response.planning.used_fallback,
        response.planning.fallback_category,
        extra={"correlation_id": str(request.state.correlation_id)},
    )
    return response


@router.post("/generate", response_model=WorkflowGenerateResponse)
def generate_workflow_operations(
    request: WorkflowGenerateRequest,
) -> WorkflowGenerateResponse:
    return generate_workflow(request)


@router.post("/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(
    file: Annotated[UploadFile, File(description="CSV dataset to transform.")],
    operation_graph: Annotated[
        str,
        Form(description="Approved operation graph JSON from /api/v1/workflows/generate."),
    ],
) -> WorkflowExecuteResponse:
    settings = get_settings()
    return await execute_workflow_upload(
        file=file,
        operation_graph_raw=operation_graph,
        max_upload_bytes=settings.max_upload_bytes,
    )
