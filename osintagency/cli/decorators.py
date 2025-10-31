"""Reusable decorators for OSINT Agency CLI commands."""

from __future__ import annotations

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from ..logging_config import configure_logging

P = ParamSpec("P")
R = TypeVar("R")


def osintagency_cli_command(*, log_level_param: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Ensure shared CLI preconditions (logging, diagnostics) run before command execution."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            level = kwargs.get(log_level_param) if log_level_param else None
            configure_logging(level)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["osintagency_cli_command"]
