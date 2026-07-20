from pathlib import Path

import polars as pl
from fastapi.testclient import TestClient

from app.lookup.service import perform_left_lookup
from app.main import create_app


def test_left_lookup_preserves_rows_and_flags_unmatched_keys() -> None:
    orders = pl.read_csv(Path("samples/lookup_orders.csv"))
    customers = pl.read_csv(Path("samples/lookup_customers.csv"))

    result = perform_left_lookup(
        left_df=orders,
        right_df=customers,
        left_key="customer_id",
        right_key="customer_id",
        lookup_columns=["customer_name", "salesforce_account_id"],
    )

    assert result.output_df.height == orders.height
    assert result.matched_row_count == 3
    assert result.unmatched_row_count == 1
    assert result.unmatched_keys == ["C999"]
    assert "lookup_matched" in result.output_df.columns
    c001_customer_name = result.output_df.filter(pl.col("customer_id") == "C001")[
        "customer_name"
    ][0]
    assert c001_customer_name == "Ada North"
    assert any("duplicate lookup key" in warning for warning in result.warnings)


def test_lookup_endpoint_accepts_two_csv_uploads() -> None:
    client = TestClient(create_app())

    with (
        Path("samples/lookup_orders.csv").open("rb") as left_file,
        Path("samples/lookup_customers.csv").open("rb") as right_file,
    ):
        response = client.post(
            "/api/v1/lookups/preview",
            files={
                "left_file": ("lookup_orders.csv", left_file, "text/csv"),
                "right_file": ("lookup_customers.csv", right_file, "text/csv"),
            },
            data={
                "left_key": "customer_id",
                "right_key": "customer_id",
                "lookup_columns": "customer_name,salesforce_account_id",
                "join_type": "left",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["output_row_count"] == 4
    assert body["unmatched_row_count"] == 1
    assert body["unmatched_keys"] == ["C999"]
