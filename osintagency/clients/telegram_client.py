"""Telegram client implementations for deterministic and live environments."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Protocol

from ..config import TelegramConfig


class TelegramMessageClient(Protocol):
    """Protocol for deterministic Telegram-like clients."""

    @property
    def requires_auth(self) -> bool:
        """Return True when the client requires authenticated configuration."""

    def fetch_messages(
        self, channel_id: str, limit: int, offset_date: datetime | None = None
    ) -> List[dict[str, object]]:
        """Return deterministic message payloads."""


class DeterministicTelegramClient:
    """Generate predictable Telegram-like messages without network access."""

    @property
    def requires_auth(self) -> bool:
        return False

    def __init__(self) -> None:
        self._base_timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)

    def fetch_messages(
        self, channel_id: str, limit: int, offset_date: datetime | None = None
    ) -> List[dict[str, object]]:
        base_label = channel_id.lstrip("@") or "channel"
        messages = [
            {
                "id": idx + 1,
                "timestamp": (
                    self._base_timestamp + timedelta(minutes=idx)
                ).isoformat(),
                "text": f"{base_label} message {idx + 1}",
            }
            for idx in range(limit)
        ]

        # Filter messages if offset_date is provided
        if offset_date is not None:
            messages = [
                msg
                for msg in messages
                if datetime.fromisoformat(msg["timestamp"]) > offset_date
            ]

        return messages


class TelethonTelegramClient:
    """Fetch real messages from Telegram using Telethon."""

    _SESSION_NAME = "osintagency"

    @property
    def requires_auth(self) -> bool:
        return True

    def __init__(self, config: TelegramConfig) -> None:
        self._config = config

    def fetch_messages(
        self, channel_id: str, limit: int, offset_date: datetime | None = None
    ) -> List[dict[str, object]]:
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
            for message in client.iter_messages(
                channel_id, limit=limit, offset_date=offset_date
            ):
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
