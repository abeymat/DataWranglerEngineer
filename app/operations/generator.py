from app.operations.models import (
    Operation,
    OperationGraph,
    OperationType,
    WorkflowGenerateRequest,
    WorkflowGenerateResponse,
)
from app.operations.polars_renderer import render_polars_code


def generate_workflow(request: WorkflowGenerateRequest) -> WorkflowGenerateResponse:
    spec = request.spec
    graph = OperationGraph(
        graph_id="customer_salesforce_import_v1",
        workflow_name=spec.workflow_name,
        operations=[
            Operation(
                operation_id="op_001",
                operation_type=OperationType.ADD_MISSING_FLAG,
                description="Flag rows where customer_id is missing.",
                input_columns=["customer_id"],
                output_columns=["missing_customer_id"],
                parameters={"source_column": "customer_id", "target_column": "missing_customer_id"},
            ),
            Operation(
                operation_id="op_002",
                operation_type=OperationType.DEDUPLICATE,
                description="Remove exact duplicate rows.",
            ),
            Operation(
                operation_id="op_003",
                operation_type=OperationType.NORMALIZE_US_PHONE,
                description="Normalize phone values to +1XXXXXXXXXX when possible.",
                input_columns=["phone"],
                output_columns=["normalized_phone"],
                parameters={"source_column": "phone", "target_column": "normalized_phone"},
            ),
            Operation(
                operation_id="op_004",
                operation_type=OperationType.CLEAN_NUMERIC_STRING,
                description="Convert purchase_amount strings into numeric decimal values.",
                input_columns=["purchase_amount"],
                output_columns=["purchase_amount_numeric"],
                parameters={
                    "source_column": "purchase_amount",
                    "target_column": "purchase_amount_numeric",
                },
            ),
            Operation(
                operation_id="op_005",
                operation_type=OperationType.PARSE_DATE,
                description="Parse transaction_date into a date column when possible.",
                input_columns=["transaction_date"],
                output_columns=["transaction_date_parsed"],
                parameters={
                    "source_column": "transaction_date",
                    "target_column": "transaction_date_parsed",
                },
            ),
            Operation(
                operation_id="op_006",
                operation_type=OperationType.GROUP_CUSTOMERS,
                description=(
                    "Create one output row per customer and aggregate addresses and purchases."
                ),
                input_columns=[
                    "customer_id",
                    "customer_name",
                    "address",
                    "normalized_phone",
                    "purchase_amount_numeric",
                    "transaction_date_parsed",
                    "missing_customer_id",
                ],
                output_columns=[
                    "address_list",
                    "total_purchases",
                    "most_recent_transaction_date",
                ],
                parameters={"grouping_keys": ["customer_id", "customer_name"]},
            ),
            Operation(
                operation_id="op_007",
                operation_type=OperationType.ADD_SALESFORCE_STATUS,
                description="Mark rows as ready or needing review before Salesforce import.",
                output_columns=["salesforce_import_status"],
            ),
            Operation(
                operation_id="op_008",
                operation_type=OperationType.SELECT_COLUMNS,
                description="Select the approved Salesforce-ready output columns.",
                output_columns=spec.output_columns,
                parameters={"columns": spec.output_columns},
            ),
            Operation(
                operation_id="op_009",
                operation_type=OperationType.SORT,
                description="Sort output for stable previews and exports.",
                parameters={"columns": ["customer_name", "customer_id"]},
            ),
        ],
        explanation=(
            "This operation graph uses only approved Polars transformations for the customer "
            "Salesforce import demo. It flags missing IDs, removes exact duplicates, normalizes "
            "phones, cleans purchase amounts, parses dates, groups customers, and selects a "
            "stable Salesforce-ready output schema."
        ),
    )
    return WorkflowGenerateResponse(operation_graph=graph, polars_code=render_polars_code(graph))
