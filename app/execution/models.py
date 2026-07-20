from typing import Any

from pydantic import BaseModel, Field

from app.salesforce.models import SalesforceLoadPlan


class ValidationFinding(BaseModel):
    rule_id: str
    status: str = Field(pattern="^(passed|warning|failed)$")
    message: str
    severity: str = Field(pattern="^(error|warning|info)$")


class ExecutionMetrics(BaseModel):
    input_row_count: int
    deduplicated_row_count: int
    output_row_count: int
    duplicate_rows_removed: int
    missing_customer_id_count: int
    invalid_phone_count: int
    source_purchase_total: float
    output_purchase_total: float


class WorkflowExecuteResponse(BaseModel):
    success: bool = True
    execution_status: str
    graph_id: str
    input_dataset: str
    output_columns: list[str]
    metrics: ExecutionMetrics
    validation_findings: list[ValidationFinding]
    salesforce_load_plan: SalesforceLoadPlan
    warnings: list[str] = Field(default_factory=list)
    preview_rows: list[dict[str, Any]]
    duration_ms: int
