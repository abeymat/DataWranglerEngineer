from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.planning.models import ModelTokenUsage, TransformationAction, WorkflowSpec

StepId = Literal[
    "step_001",
    "step_002",
    "step_003",
    "step_004",
    "step_005",
    "step_006",
    "step_007",
]
RuleId = Literal["val_001", "val_002", "val_003", "val_004", "val_005"]


class ModelPlanningOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelTransformationStep(ModelPlanningOutput):
    step_id: StepId
    action: TransformationAction
    business_description: str = Field(min_length=5, max_length=300)


class ModelValidationRule(ModelPlanningOutput):
    rule_id: RuleId
    description: str = Field(min_length=5, max_length=300)


class ModelWorkflowPlan(ModelPlanningOutput):
    workflow_name: str = Field(min_length=3, max_length=100)
    transformation_steps: list[ModelTransformationStep] = Field(min_length=7, max_length=7)
    validation_rules: list[ModelValidationRule] = Field(min_length=5, max_length=5)
    assumptions: list[str] = Field(min_length=1, max_length=10)
    warnings: list[str] = Field(default_factory=list, max_length=10)


@dataclass(frozen=True)
class OpenAIPlanResult:
    spec: WorkflowSpec
    response_id: str
    effective_model: str
    usage: ModelTokenUsage | None
