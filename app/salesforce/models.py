from enum import StrEnum

from pydantic import BaseModel, Field


class SalesforceLoadOperation(StrEnum):
    INSERT = "insert"
    UPDATE = "update"
    UPSERT = "upsert"


class SalesforceLoadTarget(BaseModel):
    system: str = "salesforce"
    object_api_name: str = "Account"
    operation: SalesforceLoadOperation = SalesforceLoadOperation.UPSERT
    external_id_field: str = "External_Id__c"


class SalesforceFieldMapping(BaseModel):
    source_column: str
    target_field: str
    required: bool = False


class SalesforceLoadPlan(BaseModel):
    target: SalesforceLoadTarget = Field(default_factory=SalesforceLoadTarget)
    output_format: str = "csv"
    field_mappings: list[SalesforceFieldMapping]
    required_output_columns: list[str]
    missing_output_columns: list[str]
    ready_for_load: bool
    notes: list[str] = Field(default_factory=list)


class SalesforceLoadPlanRequest(BaseModel):
    output_columns: list[str]
    target: SalesforceLoadTarget = Field(default_factory=SalesforceLoadTarget)


class SalesforceLoadPlanResponse(BaseModel):
    success: bool = True
    load_plan: SalesforceLoadPlan
