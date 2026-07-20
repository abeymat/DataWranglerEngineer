import csv
import io
from dataclasses import dataclass

import polars as pl
from fastapi import UploadFile

from app.core.errors import AppError

ALLOWED_CSV_EXTENSIONS = {".csv"}


@dataclass(frozen=True)
class LoadedCsv:
    filename: str
    dataframe: pl.DataFrame
    detected_delimiter: str
    encoding: str
    malformed_row_count: int


async def load_csv_upload(file: UploadFile, max_upload_bytes: int) -> LoadedCsv:
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

    text, encoding = decode_csv_bytes(content)
    delimiter = detect_delimiter(text)
    malformed_count = count_malformed_rows(text, delimiter)
    dataframe = read_csv_text(text, delimiter)
    return LoadedCsv(
        filename=filename,
        dataframe=dataframe,
        detected_delimiter=delimiter,
        encoding=encoding,
        malformed_row_count=malformed_count,
    )


def decode_csv_bytes(content: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise AppError("Could not decode CSV using supported encodings.", "encoding_error", 400)


def detect_delimiter(text: str) -> str:
    sample = text[:8192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","


def count_malformed_rows(text: str, delimiter: str) -> int:
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return 0
    expected = len(rows[0])
    return sum(1 for row in rows[1:] if len(row) != expected)


def read_csv_text(text: str, delimiter: str) -> pl.DataFrame:
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
