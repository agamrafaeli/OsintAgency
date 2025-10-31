"""Standalone routine for clearing the message store."""

from __future__ import annotations

import os

from ..collector import purge_database_file
from ..logging_config import configure_logging, get_logger
from ..storage import resolve_db_path

logger = get_logger(__name__)


def cleanup_database_action(
    *,
    db_path: str | os.PathLike[str] | None,
    log_level: str,
) -> int:
    """Delete the configured message database if it exists."""
    configure_logging(log_level)
    target = resolve_db_path(db_path)
    removed = purge_database_file(db_path=target)
    if removed:
        logger.info("Removed database at %s", target)
    else:
        logger.info("No database found at %s", target)
    return 0


__all__ = ["cleanup_database_action"]
