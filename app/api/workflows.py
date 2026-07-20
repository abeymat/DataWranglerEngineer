from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.core.settings import get_settings
from app.execution.models import WorkflowExecuteResponse
from app.execution.service import execute_workflow_upload
from app.operations.generator import generate_workflow
from app.operations.models import WorkflowGenerateRequest, WorkflowGenerateResponse
from app.planning.demo_planner import plan_workflow
from app.planning.models import WorkflowPlanRequest, WorkflowPlanResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/plan", response_model=WorkflowPlanResponse)
def create_workflow_plan(request: WorkflowPlanRequest) -> WorkflowPlanResponse:
    return plan_workflow(request)


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
