from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "Data Wrangler Engineer"
    app_version: str = "0.1.0"
    cors_origins_raw: str = Field(
        default="http://localhost:8000,http://127.0.0.1:8000",
        alias="APP_CORS_ORIGINS",
    )
    max_upload_bytes: int = 5 * 1024 * 1024
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    workflow_db_path: str = "data_wrangler.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    @field_validator("max_upload_bytes")
    @classmethod
    def validate_max_upload_bytes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("MAX_UPLOAD_BYTES must be positive")
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
