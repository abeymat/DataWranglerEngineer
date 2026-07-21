import logging
import uuid
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("salesforce_etl")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s correlation_id=%(correlation_id)s %(message)s",
)


class _CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        return True


for handler in logging.getLogger().handlers:
    handler.addFilter(_CorrelationIdFilter())


class _CorrelationAdapter(logging.LoggerAdapter[logging.Logger]):
    def process(
        self,
        msg: str,
        kwargs: MutableMapping[str, Any],
    ) -> tuple[str, MutableMapping[str, Any]]:
        kwargs.setdefault("extra", {})
        kwargs["extra"].setdefault("correlation_id", "-")
        return msg, kwargs


app_logger = _CorrelationAdapter(logger, {})


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
