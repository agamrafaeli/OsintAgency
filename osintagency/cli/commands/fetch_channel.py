"""Command facade for deterministic Telegram channel collection."""

from __future__ import annotations

from ...actions.fetch_channel_action import fetch_channel_action
from ...collector import TelegramMessageClient


def fetch_channel_command(
    *,
    limit: int,
    channel: str | None,
    db_path: str | None,
    log_level: str,
    cleanup: bool,
    telegram_client: TelegramMessageClient | None = None,
) -> int:
    """Invoke the fetch-channel action with CLI-provided arguments."""
    return fetch_channel_action(
        limit=limit,
        channel=channel,
        db_path=db_path,
        cleanup=cleanup,
        log_level=log_level,
        telegram_client=telegram_client,
    )


__all__ = ["fetch_channel_command"]
