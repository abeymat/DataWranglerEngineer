from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: str
    category: str
    correlation_id: str


class AppError(Exception):
    def __init__(self, message: str, category: str = "application_error", status_code: int = 400):
        self.message = message
        self.category = category
        self.status_code = status_code
        super().__init__(message)


def _correlation_id(request: Request) -> str:
    return str(getattr(request.state, "correlation_id", "-"))


def _envelope(request: Request, message: str, category: str) -> dict[str, str | bool]:
    return ErrorEnvelope(
        error=message,
        category=category,
        correlation_id=_correlation_id(request),
    ).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(request, exc.message, exc.category),
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(request, str(exc.detail), "http_error"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_envelope(request, str(exc.errors()), "request_validation_error"),
        )
