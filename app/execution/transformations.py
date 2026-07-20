import re
from dataclasses import dataclass

import polars as pl

from app.core.errors import AppError
from app.execution.models import ExecutionMetrics
from app.operations.models import OperationGraph, OperationType

EXPECTED_OUTPUT_COLUMNS = [
    "customer_id",
    "customer_name",
    "address_list",
    "normalized_phone",
    "total_purchases",
    "most_recent_transaction_date",
    "missing_customer_id",
    "salesforce_import_status",
]


@dataclass(frozen=True)
class TransformationResult:
    output_df: pl.DataFrame
    metrics: ExecutionMetrics


def execute_operation_graph(input_df: pl.DataFrame, graph: OperationGraph) -> TransformationResult:
    _validate_graph(graph)
    _require_columns(
        input_df,
        [
            "customer_id",
            "customer_name",
            "address",
            "phone",
            "purchase_amount",
            "transaction_date",
        ],
    )

    working_df = input_df.clone()
    input_row_count = working_df.height
    duplicate_rows_removed = input_row_count - working_df.unique(maintain_order=True).height

    working_df = working_df.with_columns(
        pl.col("customer_id").is_null().alias("missing_customer_id")
    )
    working_df = working_df.unique(maintain_order=True)

    phone_digits = pl.col("phone").cast(pl.Utf8).str.replace_all(r"\D", "")
    working_df = working_df.with_columns(
        pl.when(phone_digits.str.len_chars() == 11)
        .then(phone_digits.str.strip_prefix("1"))
        .otherwise(phone_digits)
        .alias("_phone_digits")
    ).with_columns(
        pl.when(pl.col("_phone_digits").str.len_chars() == 10)
        .then(pl.concat_str([pl.lit("+1"), pl.col("_phone_digits")]))
        .otherwise(None)
        .alias("normalized_phone")
    )

    working_df = working_df.with_columns(
        pl.col("purchase_amount")
        .cast(pl.Utf8)
        .str.replace_all(r"[$,\s]", "")
        .cast(pl.Float64, strict=False)
        .fill_null(0)
        .alias("purchase_amount_numeric")
    )

    working_df = working_df.with_columns(
        pl.coalesce(
            pl.col("transaction_date")
            .cast(pl.Utf8)
            .str.strptime(pl.Date, "%Y-%m-%d", strict=False),
            pl.col("transaction_date")
            .cast(pl.Utf8)
            .str.strptime(pl.Date, "%m/%d/%Y", strict=False),
        ).alias("transaction_date_parsed")
    )

    output_df = (
        working_df.group_by(["customer_id", "customer_name"], maintain_order=True)
        .agg(
            pl.col("address").drop_nulls().unique().str.join("; ").alias("address_list"),
            pl.col("normalized_phone").drop_nulls().first().alias("normalized_phone"),
            pl.col("purchase_amount_numeric").sum().round(2).alias("total_purchases"),
            pl.col("transaction_date_parsed").max().alias("most_recent_transaction_date"),
            pl.col("missing_customer_id").max().alias("missing_customer_id"),
        )
        .with_columns(
            pl.when(pl.col("missing_customer_id"))
            .then(pl.lit("Review - Missing Customer ID"))
            .otherwise(pl.lit("Ready for Salesforce"))
            .alias("salesforce_import_status")
        )
        .select(EXPECTED_OUTPUT_COLUMNS)
        .sort(["customer_name", "customer_id"], nulls_last=True)
    )

    source_total = float(working_df["purchase_amount_numeric"].sum() or 0)
    output_total = float(output_df["total_purchases"].sum() or 0)
    missing_id_count = int(working_df.filter(pl.col("missing_customer_id")).height)
    invalid_phone_count = _invalid_phone_count(working_df)

    return TransformationResult(
        output_df=output_df,
        metrics=ExecutionMetrics(
            input_row_count=input_row_count,
            deduplicated_row_count=working_df.height,
            output_row_count=output_df.height,
            duplicate_rows_removed=duplicate_rows_removed,
            missing_customer_id_count=missing_id_count,
            invalid_phone_count=invalid_phone_count,
            source_purchase_total=round(source_total, 2),
            output_purchase_total=round(output_total, 2),
        ),
    )


def _validate_graph(graph: OperationGraph) -> None:
    if graph.graph_id != "customer_salesforce_import_v1":
        raise AppError("Unsupported operation graph for execution.", "unsupported_graph", 400)
    operation_types = {operation.operation_type for operation in graph.operations}
    required_operations = {
        OperationType.ADD_MISSING_FLAG,
        OperationType.DEDUPLICATE,
        OperationType.NORMALIZE_US_PHONE,
        OperationType.CLEAN_NUMERIC_STRING,
        OperationType.PARSE_DATE,
        OperationType.GROUP_CUSTOMERS,
        OperationType.ADD_SALESFORCE_STATUS,
        OperationType.SELECT_COLUMNS,
        OperationType.SORT,
    }
    missing = required_operations - operation_types
    if missing:
        missing_names = ", ".join(sorted(missing))
        raise AppError(
            f"Operation graph is missing required step(s): {missing_names}",
            "invalid_graph",
            400,
        )


def _require_columns(dataframe: pl.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise AppError(
            "Input dataset is missing required column(s): " + ", ".join(missing),
            "missing_column",
            400,
        )


def _invalid_phone_count(dataframe: pl.DataFrame) -> int:
    invalid = 0
    values = dataframe.select(["phone", "normalized_phone"]).to_dicts()
    for row in values:
        if row["phone"] is None:
            continue
        digits = re.sub(r"\D", "", str(row["phone"]))
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if row["normalized_phone"] is None:
            invalid += 1
    return invalid
