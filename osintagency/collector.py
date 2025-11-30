"""Telegram collection helpers for deterministic and live environments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from .clients import TelegramMessageClient
from .config import load_telegram_config
from .storage import persist_detected_verses, persist_forwarded_channels, persist_messages, resolve_db_path
from .services import forward_detector, quran_detector


@dataclass(frozen=True)
class CollectionOutcome:
    """Summary of a message collection run."""

    channel_id: str
    stored_messages: int
    messages: List[dict[str, object]]
    db_path: Path


def _detect_verses_for_messages(messages: List[dict[str, object]]) -> list[dict[str, object]]:
    """Return verse detections for each message payload."""
    detected_rows: list[dict[str, object]] = []
    for payload in messages:
        message_id = payload.get("id")
        if message_id is None:
            continue
        try:
            detections = quran_detector.detect_verses(
                message_id=message_id,
                text=payload.get("text"),
            )
        except ValueError:
            continue
        if detections:
            detected_rows.extend(detections)
    return detected_rows


def _detect_forwards_for_messages(messages: List[dict[str, object]]) -> list[dict[str, object]]:
    """Return forward detections for each message payload."""
    detected_rows: list[dict[str, object]] = []
    for payload in messages:
        message_id = payload.get("id")
        if message_id is None:
            continue
        try:
            detections = forward_detector.detect_forwards(
                message_id=message_id,
                raw_payload=payload,
            )
        except ValueError:
            continue
        if detections:
            detected_rows.extend(detections)
    return detected_rows


def collect_messages(
    *,
    limit: int,
    channel_id: str | None = None,
    db_path: str | Path | None = None,
    telegram_client: TelegramMessageClient,
    offset_date: datetime | None = None,
) -> CollectionOutcome:
    """Persist messages using the provided Telegram client."""
    if telegram_client is None:
        raise ValueError("telegram_client must be provided for collection.")

    # Only load config if we need target_channel from it
    if channel_id is None:
        config = load_telegram_config(require_auth=telegram_client.requires_auth)
        target_channel = config.target_channel
    else:
        target_channel = channel_id

    resolved_path = resolve_db_path(db_path)
    messages = telegram_client.fetch_messages(
        target_channel, limit, offset_date=offset_date
    )
    detected_verses = _detect_verses_for_messages(messages)
    detected_forwards = _detect_forwards_for_messages(messages)
    stored = persist_messages(
        target_channel,
        messages,
        db_path=resolved_path,
    )
    persist_detected_verses(
        detected_verses,
        message_ids=[message["id"] for message in messages],
        db_path=resolved_path,
    )
    persist_forwarded_channels(
        detected_forwards,
        message_ids=[message["id"] for message in messages],
        db_path=resolved_path,
    )
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
