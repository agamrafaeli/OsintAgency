"""Centralized logging utilities for OSINT Agency agents."""

from __future__ import annotations

import logging
import sys
from typing import Any

_CONFIGURED = False
_CONSOLE_CONFIGURED = False
_CONSOLE_STDOUT: Any | None = None
_CONSOLE_STDERR: Any | None = None


class _MaxLevelFilter(logging.Filter):
    """Filter that only allows records at or below a specific level."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


def _coerce_level(level: str | int | None) -> int:
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        return getattr(logging, level.strip().upper(), logging.INFO)
    return logging.INFO


def configure_logging(level: str | int | None = None) -> None:
    """Configure application-wide logging once per process."""
    global _CONFIGURED

    if _CONFIGURED and level is None:
        return

    resolved_level = _coerce_level(level)
    root_logger = logging.getLogger()
    root_logger.setLevel(resolved_level)

    if _CONFIGURED:
        return

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(_MaxLevelFilter(logging.INFO))
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))

    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(
        logging.Formatter("%(levelname)s %(name)s: %(message)s")
    )

    root_logger.handlers.clear()
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)

    _CONFIGURED = True


def _ensure_console_logger() -> logging.Logger:
    console_logger = logging.getLogger("osintagency.console")
    console_logger.propagate = False
    console_logger.setLevel(logging.DEBUG)

    global _CONSOLE_CONFIGURED
    global _CONSOLE_STDOUT
    global _CONSOLE_STDERR
    if (
        _CONSOLE_CONFIGURED
        and _CONSOLE_STDOUT is sys.stdout
        and _CONSOLE_STDERR is sys.stderr
    ):
        return console_logger

    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(_MaxLevelFilter(logging.INFO))
    stdout_handler.setFormatter(logging.Formatter("%(message)s"))

    stderr_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(logging.Formatter("%(message)s"))

    console_logger.handlers.clear()
    console_logger.addHandler(stdout_handler)
    console_logger.addHandler(stderr_handler)

    _CONSOLE_CONFIGURED = True
    _CONSOLE_STDOUT = sys.stdout
    _CONSOLE_STDERR = sys.stderr
    return console_logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a module-specific logger."""
    return logging.getLogger(name or "osintagency")


def get_console_logger() -> logging.Logger:
    """Return the console logger for user-facing output."""
    configure_logging()
    return _ensure_console_logger()


__all__ = ["configure_logging", "get_console_logger", "get_logger"]
