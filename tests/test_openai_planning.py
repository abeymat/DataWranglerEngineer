import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import polars as pl
import pytest

from app.core.errors import AppError
from app.core.settings import Settings
from app.ingestion.csv_profiler import profile_dataframe
from app.openai_client.models import (
    ModelTransformationStep,
    ModelValidationRule,
    ModelWorkflowPlan,
    OpenAIPlanResult,
)
from app.openai_client.workflow_planner import (
    OpenAIPlanningError,
    OpenAIResponsesWorkflowPlanner,
    _ParsedWorkflowResponse,
    build_planning_context,
)
from app.planning.demo_planner import build_demo_workflow_spec
from app.planning.models import ModelTokenUsage, WorkflowPlanRequest
from app.planning.service import plan_workflow

INSTRUCTION = (
    "Create one row per customer, normalize phones, total purchases, and prepare an Account "
    "upsert for Salesforce."
)


def _request() -> WorkflowPlanRequest:
    path = Path("samples/customer_wrangling_demo.csv")
    dataframe = pl.read_csv(path, null_values=[""])
    profile = profile_dataframe(dataframe, path.name, ",", "utf-8")
    return WorkflowPlanRequest(instruction=INSTRUCTION, dataset_profile=profile)


def _model_plan() -> ModelWorkflowPlan:
    approved = build_demo_workflow_spec(_request())
    return ModelWorkflowPlan(
        workflow_name="GPT-5.6 Customer Account ETL",
        transformation_steps=[
            ModelTransformationStep(
                step_id=step.step_id,  # type: ignore[arg-type]
                action=step.action,
                business_description=f"GPT-5.6 plan: {step.business_description}",
            )
            for step in approved.transformation_steps
        ],
        validation_rules=[
            ModelValidationRule(
                rule_id=rule.rule_id,  # type: ignore[arg-type]
                description=f"GPT-5.6 check: {rule.description}",
            )
            for rule in approved.validation_rules
        ],
        assumptions=["The source represents customer purchase activity."],
        warnings=["Review missing external identifiers before loading Salesforce."],
    )


@dataclass
class _FakeUsage:
    input_tokens: int = 120
    output_tokens: int = 80
    total_tokens: int = 200


@dataclass
class _FakeResponse:
    output_parsed: ModelWorkflowPlan | None
    id: str = "resp_build_week_56"
    model: str = "gpt-5.6-sol"
    usage: _FakeUsage | None = field(default_factory=_FakeUsage)


class _FakeResponses:
    def __init__(self, output: ModelWorkflowPlan | None) -> None:
        self.output = output
        self.call: dict[str, object] = {}

    def parse(
        self,
        *,
        model: str,
        instructions: str,
        input: str,
        text_format: type[ModelWorkflowPlan],
        reasoning: dict[str, str],
        store: bool,
        max_output_tokens: int,
        verbosity: str,
        metadata: dict[str, str],
    ) -> _ParsedWorkflowResponse:
        self.call = {
            "model": model,
            "instructions": instructions,
            "input": input,
            "text_format": text_format,
            "reasoning": reasoning,
            "store": store,
            "max_output_tokens": max_output_tokens,
            "verbosity": verbosity,
            "metadata": metadata,
        }
        return cast(_ParsedWorkflowResponse, _FakeResponse(output_parsed=self.output))


class _StubPlanner:
    def plan(self, request: WorkflowPlanRequest) -> OpenAIPlanResult:
        return OpenAIPlanResult(
            spec=build_demo_workflow_spec(request),
            response_id="resp_stub",
            effective_model="gpt-5.6-sol",
            usage=ModelTokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
        )


class _FailingPlanner:
    def plan(self, request: WorkflowPlanRequest) -> OpenAIPlanResult:
        raise OpenAIPlanningError("openai_rate_limit")


def test_gpt56_planner_uses_responses_structured_output_and_explicit_reasoning() -> None:
    fake_responses = _FakeResponses(_model_plan())
    settings = Settings(openai_api_key="test-key", openai_planning_mode="openai")
    planner = OpenAIResponsesWorkflowPlanner(settings, responses=fake_responses)

    result = planner.plan(_request())

    assert fake_responses.call["model"] == "gpt-5.6-sol"
    assert fake_responses.call["reasoning"] == {"effort": "medium"}
    assert fake_responses.call["store"] is False
    assert fake_responses.call["verbosity"] == "low"
    assert fake_responses.call["text_format"] is ModelWorkflowPlan
    assert result.effective_model == "gpt-5.6-sol"
    assert result.response_id == "resp_build_week_56"
    assert result.usage is not None and result.usage.total_tokens == 200


def test_gpt56_context_excludes_file_names_samples_and_preview_rows() -> None:
    request = _request()

    payload = json.dumps(build_planning_context(request))

    assert request.dataset_profile.filename not in payload
    assert "sample_values" not in payload
    assert "preview_rows" not in payload
    for column in request.dataset_profile.columns:
        for value in column.sample_values:
            assert value not in payload


def test_model_plan_must_match_approved_step_sequence() -> None:
    model_plan = _model_plan()
    model_plan.transformation_steps.reverse()
    planner = OpenAIResponsesWorkflowPlanner(
        Settings(openai_api_key="test-key"),
        responses=_FakeResponses(model_plan),
    )

    with pytest.raises(OpenAIPlanningError, match="openai_plan_policy_rejected"):
        planner.plan(_request())


def test_auto_mode_uses_visible_local_fallback_without_api_key() -> None:
    response = plan_workflow(
        _request(),
        settings=Settings(openai_api_key=None, openai_planning_mode="auto"),
    )

    assert response.planning.provider == "local"
    assert response.planning.used_fallback is True
    assert response.planning.fallback_category == "openai_not_configured"
    assert any("GPT-5.6 Sol was not used" in warning for warning in response.spec.warnings)


def test_openai_mode_records_model_response_and_usage() -> None:
    response = plan_workflow(
        _request(),
        settings=Settings(
            openai_api_key="test-key",
            openai_planning_mode="openai",
        ),
        planner=_StubPlanner(),
    )

    assert response.planning.provider == "openai"
    assert response.planning.effective_model == "gpt-5.6-sol"
    assert response.planning.response_id == "resp_stub"
    assert response.planning.usage is not None
    assert response.planning.usage.total_tokens == 30


def test_auto_mode_fallback_is_bounded_and_reports_sanitized_category() -> None:
    response = plan_workflow(
        _request(),
        settings=Settings(
            openai_api_key="test-key",
            openai_planning_mode="auto",
        ),
        planner=_FailingPlanner(),
    )

    assert response.planning.provider == "local"
    assert response.planning.fallback_category == "openai_rate_limit"
    assert response.planning.response_id is None


def test_required_openai_mode_fails_cleanly_without_api_key() -> None:
    with pytest.raises(AppError) as exc_info:
        plan_workflow(
            _request(),
            settings=Settings(
                openai_api_key=None,
                openai_planning_mode="openai",
            ),
        )

    assert exc_info.value.category == "openai_not_configured"
    assert "OPENAI_API_KEY" in exc_info.value.message
