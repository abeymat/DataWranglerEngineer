from app.planning.models import (
    PlanningMetadata,
    TransformationAction,
    TransformationStep,
    ValidationRule,
    WorkflowPlanRequest,
    WorkflowPlanResponse,
    WorkflowSpec,
)

DEMO_REQUIRED_COLUMNS = [
    "customer_id",
    "customer_name",
    "address",
    "phone",
    "purchase_amount",
    "transaction_date",
]

DEMO_OUTPUT_COLUMNS = [
    "customer_id",
    "customer_name",
    "address_list",
    "normalized_phone",
    "total_purchases",
    "most_recent_transaction_date",
    "missing_customer_id",
    "salesforce_import_status",
]


def build_demo_workflow_spec(request: WorkflowPlanRequest) -> WorkflowSpec:
    profile = request.dataset_profile
    available_columns = {column.name for column in profile.columns}
    missing_columns = [
        column for column in DEMO_REQUIRED_COLUMNS if column not in available_columns
    ]

    warnings = list(profile.quality.warnings)
    if missing_columns:
        warnings.append(
            "The dataset is missing required column(s): " + ", ".join(missing_columns)
        )

    return WorkflowSpec(
        workflow_name="Customer Account Salesforce ETL",
        business_objective=request.instruction,
        input_dataset=profile.filename,
        extract_source="csv_upload",
        required_columns=DEMO_REQUIRED_COLUMNS,
        transformation_steps=demo_steps(),
        grouping_keys=["customer_id", "customer_name"],
        derived_columns=[
            "address_list",
            "normalized_phone",
            "missing_customer_id",
            "salesforce_import_status",
        ],
        aggregations=["sum purchase_amount as total_purchases"],
        sorting=["customer_name ascending", "customer_id ascending"],
        output_columns=DEMO_OUTPUT_COLUMNS,
        validation_rules=demo_validation_rules(),
        assumptions=[
            "Rows with missing customer IDs are retained and flagged instead of discarded.",
            "U.S. phone numbers are normalized to +1XXXXXXXXXX when ten digits are available.",
            "Purchase amounts may contain currency symbols or thousands separators.",
            "Address lists preserve unique non-null addresses per customer.",
        ],
        warnings=warnings,
    )


def plan_workflow(request: WorkflowPlanRequest) -> WorkflowPlanResponse:
    """Return the approved local plan for direct callers and no-key demos."""
    return WorkflowPlanResponse(
        spec=build_demo_workflow_spec(request),
        planning=PlanningMetadata(
            provider="local",
            effective_model="approved-local-planner",
            prompt_version="deterministic_customer_salesforce_v1",
            duration_ms=0,
        ),
    )


def demo_steps() -> list[TransformationStep]:
    return [
        TransformationStep(
            step_id="step_001",
            action=TransformationAction.FLAG_MISSING,
            business_description="Flag records that do not have a customer ID.",
            input_columns=["customer_id"],
            output_columns=["missing_customer_id"],
        ),
        TransformationStep(
            step_id="step_002",
            action=TransformationAction.DEDUPLICATE,
            business_description="Remove exact duplicate source records before aggregation.",
        ),
        TransformationStep(
            step_id="step_003",
            action=TransformationAction.NORMALIZE_PHONE,
            business_description="Normalize U.S. phone numbers for Salesforce import.",
            input_columns=["phone"],
            output_columns=["normalized_phone"],
        ),
        TransformationStep(
            step_id="step_004",
            action=TransformationAction.GROUP_ADDRESSES,
            business_description="Combine each customer's unique addresses into a readable list.",
            input_columns=["customer_id", "customer_name", "address"],
            output_columns=["address_list"],
        ),
        TransformationStep(
            step_id="step_005",
            action=TransformationAction.AGGREGATE,
            business_description="Calculate total purchases for each customer.",
            input_columns=["purchase_amount"],
            output_columns=["total_purchases"],
            parameters={"aggregation": "sum"},
        ),
        TransformationStep(
            step_id="step_006",
            action=TransformationAction.MOST_RECENT,
            business_description="Keep the most recent transaction date for each customer.",
            input_columns=["transaction_date"],
            output_columns=["most_recent_transaction_date"],
        ),
        TransformationStep(
            step_id="step_007",
            action=TransformationAction.SELECT_COLUMNS,
            business_description="Select Salesforce-ready output columns in a stable order.",
            output_columns=DEMO_OUTPUT_COLUMNS,
        ),
    ]


def demo_validation_rules() -> list[ValidationRule]:
    return [
        ValidationRule(
            rule_id="val_001",
            description="Expected Salesforce-ready output columns exist.",
            severity="error",
            columns=DEMO_OUTPUT_COLUMNS,
        ),
        ValidationRule(
            rule_id="val_002",
            description="Rows with missing customer IDs are flagged, not dropped silently.",
            severity="error",
            columns=["customer_id", "missing_customer_id"],
        ),
        ValidationRule(
            rule_id="val_003",
            description="Exact duplicate rows are removed before customer aggregation.",
            severity="warning",
        ),
        ValidationRule(
            rule_id="val_004",
            description="Purchase totals are preserved after cleaning numeric strings.",
            severity="error",
            columns=["purchase_amount", "total_purchases"],
        ),
        ValidationRule(
            rule_id="val_005",
            description="Invalid phone numbers are surfaced rather than fabricated.",
            severity="warning",
            columns=["phone", "normalized_phone"],
        ),
    ]
