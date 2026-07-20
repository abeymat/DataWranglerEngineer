from typing import Any

from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    name: str
    inferred_type: str
    null_count: int
    null_ratio: float
    unique_count: int
    sample_values: list[str] = Field(default_factory=list)
    likely_identifier: bool = False
    quality_warnings: list[str] = Field(default_factory=list)


class DatasetQuality(BaseModel):
    row_count: int
    column_count: int
    duplicate_row_count: int
    malformed_row_count: int
    warnings: list[str] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    filename: str
    detected_delimiter: str
    encoding: str
    columns: list[ColumnProfile]
    quality: DatasetQuality
    schema_fingerprint: str
    preview_rows: list[dict[str, Any]]


class DatasetProfileResponse(BaseModel):
    success: bool = True
    profile: DatasetProfile
