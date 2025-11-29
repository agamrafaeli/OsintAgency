"""Command facade for listing suspect channels from forward references."""

from __future__ import annotations

from ...actions.list_suspect_channels_action import list_suspect_channels_action


def list_suspect_channels_command(
    *,
    db_path: str | None,
    log_level: str,
    output_format: str = "table",
    min_references: int = 1,
) -> int:
    """Invoke the list-suspect-channels action with CLI-provided arguments."""
    return list_suspect_channels_action(
        db_path=db_path,
        log_level=log_level,
        output_format=output_format,
        min_references=min_references,
    )


__all__ = ["list_suspect_channels_command"]
