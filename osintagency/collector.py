"""Telegram collection helpers for deterministic and live environments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Protocol

from .config import TelegramConfig, load_telegram_config
from .storage import persist_messages, resolve_db_path


@dataclass(frozen=True)
class CollectionOutcome:
    """Summary of a message collection run."""

    channel_id: str
    stored_messages: int
    messages: List[dict[str, object]]
    db_path: Path


class TelegramMessageClient(Protocol):
    """Protocol for deterministic Telegram-like clients."""

    @property
    def requires_auth(self) -> bool:
        """Return True when the client requires authenticated configuration."""

    def fetch_messages(self, channel_id: str, limit: int) -> List[dict[str, object]]:
        """Return deterministic message payloads."""


class DeterministicTelegramClient:
    """Generate predictable Telegram-like messages without network access."""

    @property
    def requires_auth(self) -> bool:
        return False

    def __init__(self) -> None:
        self._base_timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)

    def fetch_messages(self, channel_id: str, limit: int) -> List[dict[str, object]]:
        base_label = channel_id.lstrip("@") or "channel"
        return [
            {
                "id": idx + 1,
                "timestamp": (
                    self._base_timestamp + timedelta(minutes=idx)
                ).isoformat(),
                "text": f"{base_label} message {idx + 1}",
            }
            for idx in range(limit)
        ]


class TelethonTelegramClient:
    """Fetch real messages from Telegram using Telethon."""

    _SESSION_NAME = "osintagency"

    @property
    def requires_auth(self) -> bool:
        return True

    def __init__(self, config: TelegramConfig) -> None:
        self._config = config

    def fetch_messages(self, channel_id: str, limit: int) -> List[dict[str, object]]:
        try:
            from telethon.sessions import StringSession
            from telethon.sync import TelegramClient
        except ImportError as err:
            raise RuntimeError(
                "Telethon must be installed to fetch live messages.",
            ) from err

        if self._config.session_string:
            client = TelegramClient(
                StringSession(self._config.session_string),
                self._config.api_id,
                self._config.api_hash,
            )
            start_kwargs: dict[str, object] = {}
        else:
            if not self._config.bot_token:
                raise RuntimeError(
                    "Provide TELEGRAM_BOT_TOKEN or TELEGRAM_SESSION_STRING for live collection.",
                )
            client = TelegramClient(
                self._SESSION_NAME,
                self._config.api_id,
                self._config.api_hash,
            )
            start_kwargs = {"bot_token": self._config.bot_token}

        messages: List[dict[str, object]] = []
        with client:
            if start_kwargs:
                client.start(**start_kwargs)
            else:
                client.start()
            for message in client.iter_messages(channel_id, limit=limit):
                if message is None:
                    continue
                payload = message.to_dict()
                payload["id"] = message.id
                payload["timestamp"] = (
                    message.date.isoformat()
                    if getattr(message, "date", None)
                    else None
                )
                payload["text"] = message.message or ""
                messages.append(payload)

        messages.reverse()
        return messages


def collect_messages(
    *,
    limit: int,
    channel_id: str | None = None,
    db_path: str | Path | None = None,
    telegram_client: TelegramMessageClient,
) -> CollectionOutcome:
    """Persist messages using the provided Telegram client."""
    if telegram_client is None:
        raise ValueError("telegram_client must be provided for collection.")

    config = load_telegram_config(require_auth=telegram_client.requires_auth)
    target_channel = channel_id or config.target_channel
    resolved_path = resolve_db_path(db_path)
    messages = telegram_client.fetch_messages(target_channel, limit)
    stored = persist_messages(target_channel, messages, db_path=resolved_path)
    return CollectionOutcome(
        channel_id=target_channel,
        stored_messages=stored,
        messages=messages,
        db_path=resolved_path,
    )


def purge_database_file(
    *, db_path: str | Path | None = None, missing_ok: bool = True
) -> bool:
    """Remove the Sqlite database that backs the message store."""
    resolved_path = resolve_db_path(db_path)
    if not resolved_path.exists():
        return False
    resolved_path.unlink(missing_ok=missing_ok)
    return True
