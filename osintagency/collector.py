"""Deterministic Telegram collector for local development."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

from .config import load_telegram_config
from .storage import persist_messages, resolve_db_path


@dataclass(frozen=True)
class CollectionOutcome:
    """Summary of a stubbed collection run."""

    channel_id: str
    stored_messages: int
    messages: List[dict[str, object]]
    db_path: Path


class DeterministicTelegramClient:
    """Generate predictable Telegram-like messages without network access."""

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


def collect_with_stub(
    *,
    limit: int,
    channel_override: str | None = None,
    db_path: str | Path | None = None,
) -> CollectionOutcome:
    """Persist deterministic messages using the configured channel."""
    config = load_telegram_config(require_auth=False)
    channel_id = channel_override or config.target_channel
    resolved_path = resolve_db_path(db_path)
    client = DeterministicTelegramClient()
    messages = client.fetch_messages(channel_id, limit)
    stored = persist_messages(channel_id, messages, db_path=resolved_path)
    return CollectionOutcome(
        channel_id=channel_id,
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
