from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.core.settings import get_settings
from app.ingestion.csv_profiler import profile_csv_upload
from app.ingestion.models import DatasetProfileResponse

router = APIRouter(tags=["datasets"])


@router.post("/datasets/profile", response_model=DatasetProfileResponse)
async def profile_dataset(file: Annotated[UploadFile, File(...)]) -> DatasetProfileResponse:
    settings = get_settings()
    return await profile_csv_upload(file, max_upload_bytes=settings.max_upload_bytes)
