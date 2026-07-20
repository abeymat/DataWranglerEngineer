from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.core.settings import get_settings
from app.lookup.models import LookupPreviewResponse
from app.lookup.service import run_lookup_preview

router = APIRouter(prefix="/lookups", tags=["lookups"])


@router.post("/preview", response_model=LookupPreviewResponse)
async def preview_lookup(
    left_file: Annotated[UploadFile, File(description="Primary CSV, like the Excel table.")],
    right_file: Annotated[UploadFile, File(description="Lookup CSV, like the VLOOKUP range.")],
    left_key: Annotated[str, Form(description="Column in the primary CSV to match on.")],
    right_key: Annotated[str, Form(description="Column in the lookup CSV to match on.")],
    lookup_columns: Annotated[
        str,
        Form(description="Comma-separated lookup columns to append from the lookup CSV."),
    ],
    join_type: Annotated[str, Form(description="Currently supports left joins.")] = "left",
) -> LookupPreviewResponse:
    settings = get_settings()
    return await run_lookup_preview(
        left_file=left_file,
        right_file=right_file,
        left_key=left_key,
        right_key=right_key,
        lookup_columns_raw=lookup_columns,
        join_type=join_type,
        max_upload_bytes=settings.max_upload_bytes,
    )
