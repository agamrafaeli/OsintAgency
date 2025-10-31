"""SQLite-backed persistence for raw Telegram messages."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping

DEFAULT_DB_FILENAME = "messages.sqlite3"


def persist_messages(
    channel_id: str,
    messages: Iterable[Mapping[str, object]],
    *,
    db_path: str | os.PathLike[str] | None = None,
) -> int:
    """Upsert message records into the raw message store."""
    target_path = _resolve_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    message_buffer: list[MutableMapping[str, object]] = [
        _normalize_message(payload) for payload in messages
    ]

    with sqlite3.connect(target_path) as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        _ensure_schema(conn)
        if not message_buffer:
            return 0
        conn.executemany(
            """
            INSERT INTO messages (channel_id, message_id, posted_at, text, raw_payload)
            VALUES (:channel_id, :message_id, :posted_at, :text, :raw_payload)
            ON CONFLICT(channel_id, message_id)
            DO UPDATE SET
                posted_at = excluded.posted_at,
                text = excluded.text,
                raw_payload = excluded.raw_payload
            """,
            (
                {
                    "channel_id": channel_id,
                    "message_id": message["message_id"],
                    "posted_at": message["posted_at"],
                    "text": message["text"],
                    "raw_payload": json.dumps(
                        message["raw_payload"], ensure_ascii=False
                    ),
                }
                for message in message_buffer
            ),
        )
        conn.commit()

    return len(message_buffer)


def _normalize_message(message: Mapping[str, object]) -> MutableMapping[str, object]:
    if "id" not in message:
        raise ValueError("Message payload missing 'id' field.")

    normalized: MutableMapping[str, object] = {
        "message_id": message["id"],
        "posted_at": message.get("timestamp"),
        "text": message.get("text", "") or "",
        "raw_payload": dict(message),
    }
    try:
        normalized["message_id"] = int(normalized["message_id"])
    except (TypeError, ValueError) as err:
        raise ValueError("Message 'id' must be an integer.") from err

    posted_at = normalized["posted_at"]
    if posted_at is not None and not isinstance(posted_at, str):
        normalized["posted_at"] = str(posted_at)

    text = normalized["text"]
    if not isinstance(text, str):
        normalized["text"] = str(text) if text is not None else ""

    return normalized


def _resolve_db_path(
    override: str | os.PathLike[str] | None,
) -> Path:
    if override is not None:
        return Path(override)
    env_override = os.getenv("OSINTAGENCY_DB_PATH")
    if env_override:
        return Path(env_override)
    return Path("data") / DEFAULT_DB_FILENAME


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            channel_id TEXT NOT NULL,
            message_id INTEGER NOT NULL,
            posted_at TEXT,
            text TEXT,
            raw_payload TEXT,
            PRIMARY KEY (channel_id, message_id)
        )
        """
    )
