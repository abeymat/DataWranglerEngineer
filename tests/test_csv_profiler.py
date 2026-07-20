from pathlib import Path

import polars as pl

from app.ingestion.csv_profiler import profile_dataframe


def test_customer_demo_profile_detects_quality_issues() -> None:
    path = Path("samples/customer_wrangling_demo.csv")
    dataframe = pl.read_csv(path, null_values=[""])

    profile = profile_dataframe(
        dataframe=dataframe,
        filename=path.name,
        delimiter=",",
        encoding="utf-8",
    )

    assert profile.quality.row_count == 8
    assert profile.quality.duplicate_row_count == 1
    assert profile.schema_fingerprint
    warnings = " ".join(profile.quality.warnings)
    assert "customer_id" in warnings
    assert "phone" in warnings
    assert "transaction_date" in warnings


def test_identifier_detection_for_unique_id_column() -> None:
    dataframe = pl.DataFrame({"record_id": ["R1", "R2", "R3"], "name": ["a", "b", "c"]})

    profile = profile_dataframe(
        dataframe=dataframe,
        filename="ids.csv",
        delimiter=",",
        encoding="utf-8",
    )

    record_id = next(column for column in profile.columns if column.name == "record_id")
    name = next(column for column in profile.columns if column.name == "name")
    assert record_id.likely_identifier is True
    assert name.likely_identifier is False
