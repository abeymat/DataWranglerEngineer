from enum import StrEnum

from pydantic import BaseModel, Field

from app.planning.models import WorkflowSpec


class OperationType(StrEnum):
    ADD_MISSING_FLAG = "add_missing_flag"
    DEDUPLICATE = "deduplicate"
    NORMALIZE_US_PHONE = "normalize_us_phone"
    CLEAN_NUMERIC_STRING = "clean_numeric_string"
    PARSE_DATE = "parse_date"
    GROUP_CUSTOMERS = "group_customers"
    ADD_SALESFORCE_STATUS = "add_salesforce_status"
    SELECT_COLUMNS = "select_columns"
    SORT = "sort"


class Operation(BaseModel):
    operation_id: str
    operation_type: OperationType
    description: str
    input_columns: list[str] = Field(default_factory=list)
    output_columns: list[str] = Field(default_factory=list)
    parameters: dict[str, str | list[str]] = Field(default_factory=dict)


class OperationGraph(BaseModel):
    graph_id: str
    workflow_name: str
    operations: list[Operation]
    explanation: str


class WorkflowGenerateRequest(BaseModel):
    spec: WorkflowSpec


class WorkflowGenerateResponse(BaseModel):
    success: bool = True
    operation_graph: OperationGraph
    polars_code: str
