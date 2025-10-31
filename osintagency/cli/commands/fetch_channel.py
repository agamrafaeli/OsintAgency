"""Command facade for deterministic Telegram channel collection."""

from __future__ import annotations

from ...actions.fetch_channel_action import fetch_channel_action
from ...collector import (
    DeterministicTelegramClient,
    TelegramMessageClient,
    TelethonTelegramClient,
)
from ...config import load_telegram_config


def fetch_channel_command(
    *,
    limit: int,
    channel_id: str | None,
    db_path: str | None,
    log_level: str,
    use_stub: bool,
    telegram_client: TelegramMessageClient | None = None,
) -> int:
    """Invoke the fetch-channel action with CLI-provided arguments."""

    resolved_client = telegram_client
    if use_stub:
        if not isinstance(resolved_client, DeterministicTelegramClient):
            resolved_client = DeterministicTelegramClient()
    else:
        if resolved_client is None:
            config = load_telegram_config(require_auth=True)
            resolved_client = TelethonTelegramClient(config)

    if resolved_client is None:
        raise RuntimeError("Failed to resolve a telegram client for collection.")

    return fetch_channel_action(
        limit=limit,
        channel_id=channel_id,
        db_path=db_path,
        log_level=log_level,
        telegram_client=resolved_client,
    )


__all__ = ["fetch_channel_command"]
