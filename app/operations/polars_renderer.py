from app.operations.models import OperationGraph


def render_polars_code(graph: OperationGraph) -> str:
    operation_ids = ", ".join(operation.operation_id for operation in graph.operations)
    return f'''import polars as pl


def transform(input_df: pl.DataFrame) -> pl.DataFrame:
    """Approved operation graph: {graph.graph_id}; operations: {operation_ids}."""
    working_df = input_df.clone()

    working_df = working_df.with_columns(
        pl.col("customer_id").is_null().alias("missing_customer_id")
    )

    working_df = working_df.unique(maintain_order=True)

    phone_digits = pl.col("phone").cast(pl.Utf8).str.replace_all(r"\\D", "")
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
        .str.replace_all(r"[$,\\s]", "")
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
        working_df
        .group_by(["customer_id", "customer_name"], maintain_order=True)
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
        .select([
            "customer_id",
            "customer_name",
            "address_list",
            "normalized_phone",
            "total_purchases",
            "most_recent_transaction_date",
            "missing_customer_id",
            "salesforce_import_status",
        ])
        .sort(["customer_name", "customer_id"], nulls_last=True)
    )

    return output_df
'''
