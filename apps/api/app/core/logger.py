"""
core/logger.py — Centralized structured logging.
Uses Python's logging module with a consistent format across all services.
"""

import logging
import sys
from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance for the given module name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        level = logging.DEBUG if settings.DEBUG else logging.INFO

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
