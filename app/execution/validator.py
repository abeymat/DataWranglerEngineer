import math

from app.execution.models import ExecutionMetrics, ValidationFinding
from app.execution.transformations import EXPECTED_OUTPUT_COLUMNS


def validate_execution(
    metrics: ExecutionMetrics,
    output_columns: list[str],
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    missing_columns = [column for column in EXPECTED_OUTPUT_COLUMNS if column not in output_columns]
    findings.append(
        ValidationFinding(
            rule_id="exec_val_001",
            status="failed" if missing_columns else "passed",
            severity="error",
            message=(
                "Missing output columns: " + ", ".join(missing_columns)
                if missing_columns
                else "All expected Salesforce-ready output columns are present."
            ),
        )
    )
    findings.append(
        ValidationFinding(
            rule_id="exec_val_002",
            status=(
                "passed" if metrics.output_row_count <= metrics.deduplicated_row_count else "failed"
            ),
            severity="error",
            message=(
                "Output row count is explainable after grouping."
                if metrics.output_row_count <= metrics.deduplicated_row_count
                else "Output row count exceeds the deduplicated input row count."
            ),
        )
    )
    findings.append(
        ValidationFinding(
            rule_id="exec_val_003",
            status="passed",
            severity="info",
            message=(
                f"{metrics.duplicate_rows_removed} exact duplicate row(s) removed before grouping."
            ),
        )
    )
    totals_match = math.isclose(
        metrics.source_purchase_total,
        metrics.output_purchase_total,
        rel_tol=0,
        abs_tol=0.01,
    )
    findings.append(
        ValidationFinding(
            rule_id="exec_val_004",
            status="passed" if totals_match else "failed",
            severity="error",
            message=(
                "Purchase totals reconcile after cleaning numeric strings."
                if totals_match
                else "Purchase totals do not reconcile."
            ),
        )
    )
    findings.append(
        ValidationFinding(
            rule_id="exec_val_005",
            status="warning" if metrics.missing_customer_id_count else "passed",
            severity="warning",
            message=(
                f"{metrics.missing_customer_id_count} row(s) with missing customer IDs "
                "were retained and flagged."
                if metrics.missing_customer_id_count
                else "No missing customer IDs were found."
            ),
        )
    )
    findings.append(
        ValidationFinding(
            rule_id="exec_val_006",
            status="warning" if metrics.invalid_phone_count else "passed",
            severity="warning",
            message=(
                f"{metrics.invalid_phone_count} phone value(s) could not be normalized "
                "and remain visible."
                if metrics.invalid_phone_count
                else "All non-null phone values were normalized."
            ),
        )
    )
    return findings
