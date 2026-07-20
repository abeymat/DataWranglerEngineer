from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.datasets import router as datasets_router
from app.api.lookups import router as lookups_router
from app.api.workflows import router as workflows_router
from app.core.errors import register_exception_handlers
from app.core.logging import CorrelationIdMiddleware
from app.core.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)
    project_root = Path(__file__).resolve().parent.parent
    static_dir = project_root / "app" / "static"
    samples_dir = project_root / "samples"

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Correlation-ID"],
    )

    register_exception_handlers(app)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/samples", StaticFiles(directory=samples_dir), name="samples")
    app.include_router(datasets_router, prefix="/api/v1")
    app.include_router(lookups_router, prefix="/api/v1")
    app.include_router(workflows_router, prefix="/api/v1")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name, "version": settings.app_version}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        return {"status": "ready"}

    return app


app = create_app()
