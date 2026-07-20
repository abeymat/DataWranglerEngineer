from enum import StrEnum

from pydantic import BaseModel, Field

from app.ingestion.models import DatasetProfile
from app.salesforce.models import SalesforceLoadTarget


class TransformationAction(StrEnum):
    DEDUPLICATE = "deduplicate"
    FLAG_MISSING = "flag_missing"
    NORMALIZE_PHONE = "normalize_phone"
    GROUP_ADDRESSES = "group_addresses"
    AGGREGATE = "aggregate"
    MOST_RECENT = "most_recent"
    SELECT_COLUMNS = "select_columns"
    SORT = "sort"


class TransformationStep(BaseModel):
    step_id: str
    action: TransformationAction
    business_description: str
    input_columns: list[str] = Field(default_factory=list)
    output_columns: list[str] = Field(default_factory=list)
    parameters: dict[str, str | list[str]] = Field(default_factory=dict)


class ValidationRule(BaseModel):
    rule_id: str
    description: str
    severity: str = Field(pattern="^(error|warning|info)$")
    columns: list[str] = Field(default_factory=list)


class WorkflowSpec(BaseModel):
    workflow_name: str
    business_objective: str
    input_dataset: str
    extract_source: str = "csv_upload"
    load_target: SalesforceLoadTarget = Field(default_factory=SalesforceLoadTarget)
    required_columns: list[str]
    transformation_steps: list[TransformationStep]
    grouping_keys: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    derived_columns: list[str] = Field(default_factory=list)
    aggregations: list[str] = Field(default_factory=list)
    sorting: list[str] = Field(default_factory=list)
    output_columns: list[str]
    validation_rules: list[ValidationRule]
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class WorkflowPlanRequest(BaseModel):
    instruction: str
    dataset_profile: DatasetProfile


class WorkflowPlanResponse(BaseModel):
    success: bool = True
    spec: WorkflowSpec
