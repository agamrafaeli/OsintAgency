"""Peewee-backed persistence for raw Telegram messages."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping

from peewee import EXCLUDED, SqliteDatabase

from .schema import StoredMessage, database_proxy

DEFAULT_DB_FILENAME = "messages.sqlite3"
_current_db_path: Path | None = None

def resolve_db_path(
    override: str | os.PathLike[str] | None = None,
) -> Path:
    """Public helper to resolve the active Sqlite database path."""
    return _resolve_db_path(override)


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

    database = _initialize_database(target_path)

    if not message_buffer:
        _ensure_schema()
        database.close()
        return 0

    serialized_messages = [
        {
            "channel_id": channel_id,
            "message_id": message["message_id"],
            "posted_at": message["posted_at"],
            "text": message["text"],
            "raw_payload": json.dumps(message["raw_payload"], ensure_ascii=False),
        }
        for message in message_buffer
    ]

    with database.atomic():
        _ensure_schema()
        StoredMessage.insert_many(serialized_messages).on_conflict(
            conflict_target=[StoredMessage.channel_id, StoredMessage.message_id],
            update={
                StoredMessage.posted_at: EXCLUDED.posted_at,
                StoredMessage.text: EXCLUDED.text,
                StoredMessage.raw_payload: EXCLUDED.raw_payload,
            },
        ).execute()

    database.close()

    return len(message_buffer)


def fetch_messages(
    channel_id: str | None = None,
    *,
    db_path: str | os.PathLike[str] | None = None,
) -> list[dict[str, object]]:
    """Return stored messages ordered by message id for verification and analytics."""
    target_path = _resolve_db_path(db_path)
    database = _initialize_database(target_path)
    with database.connection_context():
        _ensure_schema()
        query = StoredMessage.select().order_by(StoredMessage.message_id)
        if channel_id is not None:
            query = query.where(StoredMessage.channel_id == channel_id)
        results: list[dict[str, object]] = [
            {
                "channel_id": record.channel_id,
                "message_id": record.message_id,
                "posted_at": record.posted_at,
                "text": record.text,
                "raw_payload": json.loads(record.raw_payload),
            }
            for record in query
        ]
    database.close()
    return results


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


def _initialize_database(db_path: Path) -> SqliteDatabase:
    global _current_db_path
    should_initialize = database_proxy.obj is None or _current_db_path != db_path
    if should_initialize:
        database = SqliteDatabase(
            db_path,
            pragmas={"journal_mode": "wal", "foreign_keys": 1},
        )
        database_proxy.initialize(database)
        _current_db_path = db_path

    database = database_proxy.obj
    database.connect(reuse_if_open=True)
    return database


def _ensure_schema() -> None:
    database = database_proxy.obj
    if database is None:
        raise RuntimeError("Database has not been initialized.")
    database.create_tables([StoredMessage], safe=True)
