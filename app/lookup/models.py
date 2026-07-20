from typing import Any

from pydantic import BaseModel, Field


class LookupPreviewResponse(BaseModel):
    success: bool = True
    join_type: str
    left_dataset: str
    right_dataset: str
    left_key: str
    right_key: str
    lookup_columns: list[str]
    output_columns: list[str]
    input_row_count: int
    output_row_count: int
    matched_row_count: int
    unmatched_row_count: int
    unmatched_keys: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    preview_rows: list[dict[str, Any]]
