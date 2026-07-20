import polars as pl
from fastapi import UploadFile

from app.core.errors import AppError
from app.ingestion.csv_loader import load_csv_upload
from app.lookup.models import LookupPreviewResponse

MATCH_MARKER = "__lookup_matched"
PREVIEW_LIMIT = 25
UNMATCHED_KEY_LIMIT = 10


async def run_lookup_preview(
    left_file: UploadFile,
    right_file: UploadFile,
    left_key: str,
    right_key: str,
    lookup_columns_raw: str,
    join_type: str,
    max_upload_bytes: int,
) -> LookupPreviewResponse:
    if join_type.lower() != "left":
        raise AppError(
            "Only left lookup joins are supported right now.",
            "unsupported_join_type",
            400,
        )

    left = await load_csv_upload(left_file, max_upload_bytes=max_upload_bytes)
    right = await load_csv_upload(right_file, max_upload_bytes=max_upload_bytes)
    lookup_columns = _parse_lookup_columns(lookup_columns_raw)

    result = perform_left_lookup(
        left_df=left.dataframe,
        right_df=right.dataframe,
        left_key=left_key,
        right_key=right_key,
        lookup_columns=lookup_columns,
    )

    return LookupPreviewResponse(
        join_type="left",
        left_dataset=left.filename,
        right_dataset=right.filename,
        left_key=left_key,
        right_key=right_key,
        lookup_columns=result.lookup_output_columns,
        output_columns=result.output_df.columns,
        input_row_count=left.dataframe.height,
        output_row_count=result.output_df.height,
        matched_row_count=result.matched_row_count,
        unmatched_row_count=result.unmatched_row_count,
        unmatched_keys=result.unmatched_keys,
        warnings=result.warnings,
        preview_rows=result.output_df.head(PREVIEW_LIMIT).to_dicts(),
    )


class LookupResult:
    def __init__(
        self,
        output_df: pl.DataFrame,
        lookup_output_columns: list[str],
        matched_row_count: int,
        unmatched_row_count: int,
        unmatched_keys: list[str],
        warnings: list[str],
    ) -> None:
        self.output_df = output_df
        self.lookup_output_columns = lookup_output_columns
        self.matched_row_count = matched_row_count
        self.unmatched_row_count = unmatched_row_count
        self.unmatched_keys = unmatched_keys
        self.warnings = warnings


def perform_left_lookup(
    left_df: pl.DataFrame,
    right_df: pl.DataFrame,
    left_key: str,
    right_key: str,
    lookup_columns: list[str],
) -> LookupResult:
    _require_column(left_df, left_key, "primary")
    _require_column(right_df, right_key, "lookup")
    for column in lookup_columns:
        _require_column(right_df, column, "lookup")

    if not lookup_columns:
        lookup_columns = [column for column in right_df.columns if column != right_key]
    if not lookup_columns:
        raise AppError(
            "Choose at least one lookup column to append.",
            "missing_lookup_columns",
            400,
        )

    warnings: list[str] = []
    duplicate_lookup_key_count = right_df.height - right_df.unique(
        subset=[right_key],
        maintain_order=True,
    ).height
    if duplicate_lookup_key_count:
        warnings.append(
            f"{duplicate_lookup_key_count} duplicate lookup key row(s) were collapsed "
            "using the first value, matching spreadsheet VLOOKUP behavior."
        )

    right_deduped = right_df.unique(subset=[right_key], keep="first", maintain_order=True)
    select_exprs: list[pl.Expr] = [pl.col(right_key)]
    lookup_output_columns: list[str] = []
    for column in lookup_columns:
        output_column = _output_column_name(column, left_df.columns, lookup_output_columns)
        lookup_output_columns.append(output_column)
        select_exprs.append(pl.col(column).alias(output_column))

    right_prepared = right_deduped.select(select_exprs).with_columns(
        pl.lit(True).alias(MATCH_MARKER)
    )
    output_df = left_df.join(right_prepared, left_on=left_key, right_on=right_key, how="left")

    unmatched_mask = pl.col(MATCH_MARKER).is_null()
    unmatched_df = output_df.filter(unmatched_mask)
    unmatched_count = unmatched_df.height
    matched_count = output_df.height - unmatched_count
    unmatched_keys = _string_values(
        unmatched_df[left_key].drop_nulls().unique().head(UNMATCHED_KEY_LIMIT)
    )
    if unmatched_count:
        warnings.append(f"{unmatched_count} primary row(s) did not find a lookup match.")

    output_df = output_df.with_columns(
        pl.col(MATCH_MARKER).fill_null(False).alias("lookup_matched")
    )
    ordered_columns = [
        *left_df.columns,
        *lookup_output_columns,
        "lookup_matched",
    ]
    output_df = output_df.select(ordered_columns)

    return LookupResult(
        output_df=output_df,
        lookup_output_columns=lookup_output_columns,
        matched_row_count=matched_count,
        unmatched_row_count=unmatched_count,
        unmatched_keys=unmatched_keys,
        warnings=warnings,
    )


def _parse_lookup_columns(raw: str) -> list[str]:
    return [column.strip() for column in raw.split(",") if column.strip()]


def _require_column(dataframe: pl.DataFrame, column: str, dataset_role: str) -> None:
    if column not in dataframe.columns:
        raise AppError(
            f"The {dataset_role} dataset does not contain column '{column}'.",
            "missing_column",
            400,
        )


def _output_column_name(column: str, left_columns: list[str], existing_outputs: list[str]) -> str:
    if column not in left_columns and column not in existing_outputs:
        return column
    candidate = f"lookup_{column}"
    suffix = 2
    while candidate in left_columns or candidate in existing_outputs:
        candidate = f"lookup_{column}_{suffix}"
        suffix += 1
    return candidate


def _string_values(series: pl.Series) -> list[str]:
    return [str(value) for value in series.to_list()]
