"""Command facade for purging the message store."""

from __future__ import annotations

from ...actions.cleanup_database_action import cleanup_database_action


def cleanup_database_command(
    *,
    db_path: str | None,
    log_level: str,
) -> int:
    """Invoke the cleanup action with CLI-provided arguments."""
    return cleanup_database_action(
        db_path=db_path,
        log_level=log_level,
    )


__all__ = ["cleanup_database_command"]
