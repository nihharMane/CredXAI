"""Shared, privacy-conscious request logging for the active FastAPI services."""

from contextvars import ContextVar
import logging
import os
import re
import time
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

CORRELATION_ID_HEADER = "X-Correlation-ID"
correlation_id_context: ContextVar[str] = ContextVar("credxai_correlation_id", default="-")
_VALID_CORRELATION_ID = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_context.get()
        return True


def configure_logging() -> None:
    """Format app and Uvicorn logs consistently without installing duplicate handlers."""
    level_name = os.getenv("CREDXAI_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(logging.StreamHandler())

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s [%(correlation_id)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    filter_instance = CorrelationIdFilter()
    configured_handlers = set()
    for logger_name in (None, "uvicorn", "uvicorn.error", "uvicorn.access"):
        current_logger = logging.getLogger(logger_name)
        for handler in current_logger.handlers:
            if handler in configured_handlers:
                continue
            configured_handlers.add(handler)
            handler.setFormatter(formatter)
            if not any(isinstance(existing, CorrelationIdFilter) for existing in handler.filters):
                handler.addFilter(filter_instance)
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)


class CorrelationIdMiddleware:
    """Validate or replace the incoming request ID and echo it on every response."""

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("credxai.http")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = next(
            (value.decode("latin-1") for name, value in scope.get("headers", [])
             if name.lower() == CORRELATION_ID_HEADER.lower().encode("ascii")),
            None,
        )
        correlation_id = incoming if incoming and _VALID_CORRELATION_ID.fullmatch(incoming) else uuid4().hex
        if incoming is not None and correlation_id != incoming:
            self.logger.warning("invalid correlation ID replaced at request boundary")

        token = correlation_id_context.set(correlation_id)
        started_at = time.perf_counter()
        status_code = 500

        async def send_with_correlation(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = [
                    (name, value) for name, value in message.get("headers", [])
                    if name.lower() != CORRELATION_ID_HEADER.lower().encode("ascii")
                ]
                headers.append((CORRELATION_ID_HEADER.lower().encode("ascii"), correlation_id.encode("ascii")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_correlation)
        finally:
            self.logger.debug(
                "http request completed method=%s status=%s duration_ms=%.1f",
                scope.get("method", "UNKNOWN"), status_code, (time.perf_counter() - started_at) * 1000,
            )
            correlation_id_context.reset(token)


def install_request_logging(app, service_name: str) -> None:
    app.add_middleware(CorrelationIdMiddleware)

    @app.exception_handler(RequestValidationError)
    async def log_validation_error(request: Request, exception: RequestValidationError):
        errors = []
        field_names = []
        for item in exception.errors():
            location = item.get("loc", ())
            safe_location = [str(part) for part in location if isinstance(part, (str, int))]
            field_names.append(".".join(safe_location))
            errors.append({
                "loc": safe_location,
                "msg": item.get("msg", "Invalid value"),
                "type": item.get("type", "value_error"),
            })
        logger = logging.getLogger(f"credxai.{service_name}")
        logger.warning(
            "prediction request validation failed field_count=%s fields=%s",
            len(field_names), ",".join(field_names[:12]),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": errors,
                "correlation_id": correlation_id_context.get(),
            },
        )


def log_prediction_endpoint(service_name: str, model_name: str):
    """Log inference lifecycle without recording request values or predictions."""
    from functools import wraps

    def decorate(endpoint):
        @wraps(endpoint)
        def logged_endpoint(*args, **kwargs):
            logger = logging.getLogger(f"credxai.{service_name}")
            started_at = time.perf_counter()
            logger.debug("prediction request accepted model=%s", model_name)
            try:
                result = endpoint(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as exc:
                logger.exception(
                    "prediction failed model=%s exception_type=%s duration_ms=%.1f",
                    model_name, type(exc).__name__, (time.perf_counter() - started_at) * 1000,
                )
                raise HTTPException(status_code=500, detail="Prediction could not be completed.") from exc
            logger.info(
                "prediction completed model=%s model_version=%s duration_ms=%.1f",
                model_name, result.get("model_version") if isinstance(result, dict) else "unknown",
                (time.perf_counter() - started_at) * 1000,
            )
            return result
        return logged_endpoint
    return decorate
