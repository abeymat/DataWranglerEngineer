import time

from app.core.errors import AppError
from app.core.settings import Settings, get_settings
from app.openai_client.workflow_planner import (
    PROMPT_VERSION,
    OpenAIPlanningError,
    OpenAIResponsesWorkflowPlanner,
    WorkflowPlanClient,
)
from app.planning.demo_planner import build_demo_workflow_spec
from app.planning.models import PlanningMetadata, WorkflowPlanRequest, WorkflowPlanResponse

LOCAL_PROMPT_VERSION = "deterministic_customer_salesforce_v1"


def plan_workflow(
    request: WorkflowPlanRequest,
    settings: Settings | None = None,
    planner: WorkflowPlanClient | None = None,
) -> WorkflowPlanResponse:
    active_settings = settings or get_settings()
    start = time.perf_counter()

    if active_settings.openai_planning_mode == "deterministic":
        return _local_response(request, active_settings, start)

    if active_settings.openai_api_key is None:
        if active_settings.openai_planning_mode == "openai":
            raise AppError(
                "GPT-5.6 Sol planning requires OPENAI_API_KEY.",
                "openai_not_configured",
                503,
            )
        return _local_response(
            request,
            active_settings,
            start,
            fallback_category="openai_not_configured",
        )

    active_planner = planner or OpenAIResponsesWorkflowPlanner(active_settings)
    try:
        result = active_planner.plan(request)
    except OpenAIPlanningError as exc:
        if active_settings.openai_planning_mode == "openai":
            raise AppError(
                "GPT-5.6 Sol could not produce an approved ETL plan. Check the model "
                "configuration and retry.",
                exc.category,
                503,
            ) from exc
        return _local_response(
            request,
            active_settings,
            start,
            fallback_category=exc.category,
        )

    return WorkflowPlanResponse(
        spec=result.spec,
        planning=PlanningMetadata(
            provider="openai",
            requested_model=active_settings.openai_model,
            effective_model=result.effective_model,
            reasoning_effort=active_settings.openai_reasoning_effort,
            prompt_version=PROMPT_VERSION,
            response_id=result.response_id,
            duration_ms=_duration_ms(start),
            usage=result.usage,
        ),
    )


def _local_response(
    request: WorkflowPlanRequest,
    settings: Settings,
    start: float,
    fallback_category: str | None = None,
) -> WorkflowPlanResponse:
    spec = build_demo_workflow_spec(request)
    if fallback_category:
        spec = spec.model_copy(
            update={
                "warnings": [
                    *spec.warnings,
                    "GPT-5.6 Sol was not used for this plan; the approved local planner "
                    "provided the deterministic workflow.",
                ]
            }
        )
    return WorkflowPlanResponse(
        spec=spec,
        planning=PlanningMetadata(
            provider="local",
            requested_model=settings.openai_model,
            effective_model="approved-local-planner",
            prompt_version=LOCAL_PROMPT_VERSION,
            used_fallback=fallback_category is not None,
            fallback_category=fallback_category,
            duration_ms=_duration_ms(start),
        ),
    )


def _duration_ms(start: float) -> int:
    return max(0, int((time.perf_counter() - start) * 1_000))
