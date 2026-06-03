from __future__ import annotations

import structlog

from .settings import settings


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer() if not settings.logging.json_format
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger(name or __name__)
