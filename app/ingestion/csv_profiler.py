import csv
import hashlib
import io
import re
from collections import Counter
from datetime import datetime
from typing import Any

import polars as pl
from fastapi import UploadFile

from app.core.errors import AppError
from app.ingestion.models import (
    ColumnProfile,
    DatasetProfile,
    DatasetProfileResponse,
    DatasetQuality,
)

ALLOWED_CSV_EXTENSIONS = {".csv"}
SAMPLE_LIMIT = 5


async def profile_csv_upload(file: UploadFile, max_upload_bytes: int) -> DatasetProfileResponse:
    filename = file.filename or "uploaded.csv"
    if not filename.lower().endswith(tuple(ALLOWED_CSV_EXTENSIONS)):
        raise AppError(
            "Only CSV uploads are supported in this version.",
            "unsupported_file_type",
            415,
        )

    content = await file.read()
    if len(content) > max_upload_bytes:
        raise AppError("Uploaded file exceeds the configured size limit.", "file_too_large", 413)
    if not content:
        raise AppError("Uploaded file is empty.", "empty_file", 400)

    text, encoding = _decode_csv_bytes(content)
    delimiter = _detect_delimiter(text)
    malformed_count = _count_malformed_rows(text, delimiter)
    dataframe = _read_csv(text, delimiter)

    profile = profile_dataframe(
        dataframe=dataframe,
        filename=filename,
        delimiter=delimiter,
        encoding=encoding,
        malformed_row_count=malformed_count,
    )
    return DatasetProfileResponse(profile=profile)


def profile_dataframe(
    dataframe: pl.DataFrame,
    filename: str,
    delimiter: str,
    encoding: str,
    malformed_row_count: int = 0,
) -> DatasetProfile:
    warnings: list[str] = []
    if dataframe.height == 0:
        warnings.append("Dataset has headers but no data rows.")
    if malformed_row_count:
        warnings.append(f"{malformed_row_count} row(s) have an unexpected number of fields.")

    duplicate_count = dataframe.height - dataframe.unique(maintain_order=True).height
    if duplicate_count:
        warnings.append(f"{duplicate_count} exact duplicate row(s) detected.")

    columns = [_profile_column(dataframe, column) for column in dataframe.columns]
    for column in columns:
        warnings.extend(f"{column.name}: {warning}" for warning in column.quality_warnings)

    schema_fingerprint = _schema_fingerprint(dataframe)
    return DatasetProfile(
        filename=filename,
        detected_delimiter=delimiter,
        encoding=encoding,
        columns=columns,
        quality=DatasetQuality(
            row_count=dataframe.height,
            column_count=dataframe.width,
            duplicate_row_count=duplicate_count,
            malformed_row_count=malformed_row_count,
            warnings=warnings,
        ),
        schema_fingerprint=schema_fingerprint,
        preview_rows=dataframe.head(SAMPLE_LIMIT).to_dicts(),
    )


def _decode_csv_bytes(content: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise AppError("Could not decode CSV using supported encodings.", "encoding_error", 400)


def _detect_delimiter(text: str) -> str:
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","


def _count_malformed_rows(text: str, delimiter: str) -> int:
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return 0
    expected = len(rows[0])
    return sum(1 for row in rows[1:] if len(row) != expected)


def _read_csv(text: str, delimiter: str) -> pl.DataFrame:
    try:
        return pl.read_csv(
            io.BytesIO(text.encode("utf-8")),
            separator=delimiter,
            infer_schema_length=200,
            ignore_errors=False,
            null_values=["", "NULL", "null", "None", "N/A", "n/a"],
        )
    except Exception as exc:
        raise AppError(
            "CSV parsing failed. No records were discarded; fix the file and try again.",
            "csv_parse_error",
            400,
        ) from exc


def _profile_column(dataframe: pl.DataFrame, column: str) -> ColumnProfile:
    series = dataframe[column]
    null_count = int(series.null_count())
    unique_count = int(series.n_unique())
    sample_values = _sample_values(series)
    warnings = _column_warnings(series, column, null_count)
    return ColumnProfile(
        name=column,
        inferred_type=str(series.dtype),
        null_count=null_count,
        null_ratio=round(null_count / dataframe.height, 4) if dataframe.height else 0,
        unique_count=unique_count,
        sample_values=sample_values,
        likely_identifier=_likely_identifier(column, dataframe.height, null_count, unique_count),
        quality_warnings=warnings,
    )


def _sample_values(series: pl.Series) -> list[str]:
    values: list[str] = []
    for value in series.drop_nulls().head(SAMPLE_LIMIT).to_list():
        values.append(_redact_value(value))
    return values


def _redact_value(value: Any) -> str:
    text = str(value)
    if re.fullmatch(r"[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}", text):
        return "<email>"
    digits = re.sub(r"\D", "", text)
    if len(digits) >= 10 and len(digits) >= len(text) / 2:
        return "<phone>"
    return text[:80]


def _column_warnings(series: pl.Series, column: str, null_count: int) -> list[str]:
    warnings: list[str] = []
    name = column.lower()
    if null_count:
        warnings.append(f"{null_count} null value(s)")
    if "phone" in name:
        invalid = _count_invalid_phone_values(series)
        if invalid:
            warnings.append(f"{invalid} value(s) do not look like U.S. phone numbers")
    if "date" in name:
        invalid_dates = _count_invalid_dates(series)
        if invalid_dates:
            warnings.append(f"{invalid_dates} value(s) could not be parsed as dates")
    if any(token in name for token in ("amount", "total", "purchase", "revenue")):
        stringy_numbers = _count_string_numeric_values(series)
        if stringy_numbers:
            warnings.append(f"{stringy_numbers} numeric-looking value(s) are stored as strings")
    if series.dtype == pl.String and series.n_unique() <= max(3, series.len() // 4):
        counts = Counter(str(value) for value in series.drop_nulls().to_list())
        rare = [value for value, count in counts.items() if count == 1]
        if rare and len(counts) > 3:
            warnings.append("contains rare categories that may need review")
    return warnings


def _count_invalid_phone_values(series: pl.Series) -> int:
    invalid = 0
    for value in series.drop_nulls().to_list():
        digits = re.sub(r"\D", "", str(value))
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if len(digits) != 10:
            invalid += 1
    return invalid


def _count_invalid_dates(series: pl.Series) -> int:
    invalid = 0
    for value in series.drop_nulls().to_list():
        if not _looks_like_date(str(value)):
            invalid += 1
    return invalid


def _looks_like_date(value: str) -> bool:
    formats = ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d")
    for date_format in formats:
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            continue
    return False


def _count_string_numeric_values(series: pl.Series) -> int:
    if series.dtype != pl.String:
        return 0
    count = 0
    for value in series.drop_nulls().to_list():
        if re.fullmatch(r"\$?\s*-?\d+(,\d{3})*(\.\d+)?", str(value).strip()):
            count += 1
    return count


def _likely_identifier(column: str, row_count: int, null_count: int, unique_count: int) -> bool:
    name = column.lower()
    looks_named = "id" in name or name.endswith("_key") or name.endswith("key")
    mostly_unique = row_count > 0 and unique_count / row_count >= 0.9
    return looks_named and null_count == 0 and mostly_unique


def _schema_fingerprint(dataframe: pl.DataFrame) -> str:
    schema_text = "|".join(f"{name}:{dtype}" for name, dtype in dataframe.schema.items())
    return hashlib.sha256(schema_text.encode("utf-8")).hexdigest()
