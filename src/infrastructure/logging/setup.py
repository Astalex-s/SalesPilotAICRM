"""
Structured JSON logging setup.

Call configure_logging() once at application startup (main.py module level).
All loggers created with logging.getLogger(__name__) will automatically
emit JSON-formatted records to stdout.

request_id_var is a ContextVar populated per-request by RequestIdMiddleware.
Every log record emitted during a request will include the request_id field.
"""
import logging
import sys
from contextvars import ContextVar

from pythonjsonlogger import jsonlogger

# Populated by RequestIdMiddleware; default "-" outside request context
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class _JsonFormatter(jsonlogger.JsonFormatter):
    """Emits log records as single-line JSON with a stable field order."""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Normalise field names
        log_record["timestamp"] = self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ")
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["request_id"] = request_id_var.get()

        # Remove duplicates added by the base class
        for key in ("levelname", "name", "asctime"):
            log_record.pop(key, None)


def configure_logging(log_level: str = "INFO") -> None:
    """Configure the root logger to emit JSON to stdout.

    Safe to call multiple times (idempotent — clears existing handlers first).
    Also silences noisy third-party access loggers that duplicate uvicorn output.
    """
    formatter = _JsonFormatter(fmt="%(message)s %(levelname)s %(name)s")

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(log_level.upper())
    root.handlers.clear()
    root.addHandler(handler)

    # Prevent double-logging from uvicorn / gunicorn access loggers
    for noisy in ("uvicorn.access", "gunicorn.access"):
        logging.getLogger(noisy).propagate = False
