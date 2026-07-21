from app.openai_client.models import ModelWorkflowPlan
from app.planning.demo_planner import build_demo_workflow_spec
from app.planning.models import WorkflowPlanRequest, WorkflowSpec


def build_approved_model_spec(
    request: WorkflowPlanRequest,
    model_plan: ModelWorkflowPlan,
) -> WorkflowSpec:
    approved = build_demo_workflow_spec(request)
    expected_steps = [(step.step_id, step.action) for step in approved.transformation_steps]
    model_steps = [(step.step_id, step.action) for step in model_plan.transformation_steps]
    if model_steps != expected_steps:
        raise ValueError("Model steps do not match the approved operation sequence")

    expected_rule_ids = [rule.rule_id for rule in approved.validation_rules]
    model_rule_ids = [rule.rule_id for rule in model_plan.validation_rules]
    if model_rule_ids != expected_rule_ids:
        raise ValueError("Model validation rules do not match the approved checks")

    step_descriptions: dict[str, str] = {
        step.step_id: step.business_description for step in model_plan.transformation_steps
    }
    validation_descriptions: dict[str, str] = {
        rule.rule_id: rule.description for rule in model_plan.validation_rules
    }
    warnings = list(
        dict.fromkeys(
            [
                *approved.warnings,
                *model_plan.warnings,
            ]
        )
    )
    return approved.model_copy(
        update={
            "workflow_name": model_plan.workflow_name,
            "business_objective": request.instruction,
            "input_dataset": request.dataset_profile.filename,
            "transformation_steps": [
                step.model_copy(
                    update={"business_description": step_descriptions[step.step_id]}
                )
                for step in approved.transformation_steps
            ],
            "validation_rules": [
                rule.model_copy(
                    update={"description": validation_descriptions[rule.rule_id]}
                )
                for rule in approved.validation_rules
            ],
            "assumptions": model_plan.assumptions,
            "warnings": warnings,
        }
    )
