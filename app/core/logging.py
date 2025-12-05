"""Logging utilities using Loguru."""

from __future__ import annotations

import logging
import sys
from typing import Optional

try:
    from loguru import logger  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("app")
    logger.warning("Loguru not available. Falling back to standard logging.")

from app.core.config import settings

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def configure_logging(log_level: Optional[str] = None) -> None:
    """Configure global logger."""

    if "loguru" not in sys.modules:
        # Already configured by logging.basicConfig
        return

    # Remove default handlers to avoid duplication
    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level or settings.LOG_LEVEL,
        format=LOG_FORMAT,
        enqueue=True,
        backtrace=False,
        diagnose=settings.DEBUG,
    )


# Initialize logging on import
configure_logging()
