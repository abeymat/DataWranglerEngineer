from fastapi import APIRouter

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
