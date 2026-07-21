import json
from pathlib import Path
from typing import Protocol, cast

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    PermissionDeniedError,
    RateLimitError,
)
from pydantic import ValidationError

from app.core.settings import Settings
from app.openai_client.models import ModelWorkflowPlan, OpenAIPlanResult
from app.planning.models import ModelTokenUsage, WorkflowPlanRequest
from app.planning.policy import build_approved_model_spec

PROMPT_VERSION = "workflow_planner_v1"


class OpenAIPlanningError(Exception):
    def __init__(self, category: str):
        self.category = category
        super().__init__(category)


class WorkflowPlanClient(Protocol):
    def plan(self, request: WorkflowPlanRequest) -> OpenAIPlanResult: ...


class _Usage(Protocol):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class _ParsedWorkflowResponse(Protocol):
    id: str
    model: str
    output_parsed: ModelWorkflowPlan | None
    usage: _Usage | None


class _ResponsesParser(Protocol):
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
    ) -> _ParsedWorkflowResponse: ...


class OpenAIResponsesWorkflowPlanner:
    def __init__(
        self,
        settings: Settings,
        responses: _ResponsesParser | None = None,
    ) -> None:
        self._settings = settings
        if responses is not None:
            self._responses = responses
            return

        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )
        self._responses = cast(_ResponsesParser, client.responses)

    def plan(self, request: WorkflowPlanRequest) -> OpenAIPlanResult:
        try:
            response = self._responses.parse(
                model=self._settings.openai_model,
                instructions=_load_prompt(),
                input=json.dumps(build_planning_context(request), sort_keys=True),
                text_format=ModelWorkflowPlan,
                reasoning={"effort": self._settings.openai_reasoning_effort},
                store=False,
                max_output_tokens=self._settings.openai_max_output_tokens,
                verbosity="low",
                metadata={
                    "product": "salesforce_etl_engineer",
                    "prompt_version": PROMPT_VERSION,
                },
            )
        except (ValidationError, ValueError) as exc:
            raise OpenAIPlanningError("openai_invalid_structured_output") from exc
        except OpenAIError as exc:
            raise OpenAIPlanningError(_classify_openai_error(exc)) from exc

        if response.output_parsed is None:
            raise OpenAIPlanningError("openai_missing_structured_output")

        try:
            spec = build_approved_model_spec(request, response.output_parsed)
        except ValueError as exc:
            raise OpenAIPlanningError("openai_plan_policy_rejected") from exc

        usage = response.usage
        token_usage = (
            ModelTokenUsage(
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.total_tokens,
            )
            if usage is not None
            else None
        )
        return OpenAIPlanResult(
            spec=spec,
            response_id=response.id,
            effective_model=response.model,
            usage=token_usage,
        )


def build_planning_context(request: WorkflowPlanRequest) -> dict[str, object]:
    profile = request.dataset_profile
    return {
        "business_instruction": request.instruction,
        "dataset_schema": {
            "schema_fingerprint": profile.schema_fingerprint,
            "row_count": profile.quality.row_count,
            "column_count": profile.quality.column_count,
            "duplicate_row_count": profile.quality.duplicate_row_count,
            "malformed_row_count": profile.quality.malformed_row_count,
            "quality_warnings": profile.quality.warnings,
            "columns": [
                {
                    "name": column.name,
                    "inferred_type": column.inferred_type,
                    "null_count": column.null_count,
                    "null_ratio": column.null_ratio,
                    "unique_count": column.unique_count,
                    "likely_identifier": column.likely_identifier,
                    "quality_warnings": column.quality_warnings,
                }
                for column in profile.columns
            ],
        },
        "approved_load_contract": {
            "system": "salesforce",
            "object": "Account",
            "operation": "upsert",
            "external_id_field": "External_Id__c",
        },
    }


def _load_prompt() -> str:
    prompt_path = Path(__file__).resolve().parents[2] / "prompts" / f"{PROMPT_VERSION}.md"
    return prompt_path.read_text(encoding="utf-8")


def _classify_openai_error(exc: OpenAIError) -> str:
    if isinstance(exc, AuthenticationError):
        return "openai_authentication"
    if isinstance(exc, PermissionDeniedError):
        return "openai_permission"
    if isinstance(exc, RateLimitError):
        return "openai_rate_limit"
    if isinstance(exc, APITimeoutError):
        return "openai_timeout"
    if isinstance(exc, APIConnectionError):
        return "openai_connection"
    if isinstance(exc, APIStatusError) and exc.status_code >= 500:
        return "openai_server_error"
    if isinstance(exc, APIStatusError):
        return "openai_request_rejected"
    return "openai_error"
