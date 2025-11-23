from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping

from peewee import EXCLUDED, SqliteDatabase

from osintagency.schema import DetectedVerse, StoredMessage, database_proxy
from osintagency.storage.interface import StorageBackend
from osintagency.storage.normalization import (
    json_default,
    normalize_detected_verses,
    normalize_message,
)

DEFAULT_DB_FILENAME = "messages.sqlite3"

class PeeweeStorage(StorageBackend):
    """Peewee-backed persistence for raw Telegram messages."""

    _active_db_path: Path | None = None

    def __init__(self, db_path: str | os.PathLike[str] | None = None):
        self.db_path = self._resolve_db_path(db_path)

    def persist_messages(
        self,
        channel_id: str,
        messages: Iterable[Mapping[str, object]],
    ) -> int:
        """Upsert message records into the raw message store."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        message_buffer: list[MutableMapping[str, object]] = [
            normalize_message(payload) for payload in messages
        ]

        database = self._initialize_database()

        if not message_buffer:
            self._ensure_schema()
            database.close()
            return 0

        serialized_messages = [
            {
                "channel_id": channel_id,
                "message_id": message["message_id"],
                "posted_at": message["posted_at"],
                "text": message["text"],
                "raw_payload": json.dumps(
                    message["raw_payload"],
                    ensure_ascii=False,
                    default=json_default,
                ),
            }
            for message in message_buffer
        ]

        with database.atomic():
            self._ensure_schema()
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
        self,
        channel_id: str | None = None,
    ) -> list[dict[str, object]]:
        """Return stored messages ordered by message id for verification and analytics."""
        database = self._initialize_database()
        with database.connection_context():
            self._ensure_schema()
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

    def persist_detected_verses(
        self,
        detected_verses: Iterable[Mapping[str, object]],
        *,
        message_ids: Iterable[int | str] | None = None,
    ) -> int:
        """Upsert detected verse rows independently from message storage."""
        database = self._initialize_database()

        normalized_rows, refresh_ids = normalize_detected_verses(
            detected_verses, message_ids
        )

        if not refresh_ids and not normalized_rows:
            self._ensure_schema()
            database.close()
            return 0

        with database.atomic():
            self._ensure_schema()
            if refresh_ids:
                (
                    DetectedVerse.delete()
                    .where(DetectedVerse.message_id.in_(refresh_ids))
                    .execute()
                )
            if normalized_rows:
                DetectedVerse.insert_many(normalized_rows).execute()

        database.close()
        return len(normalized_rows)

    def _resolve_db_path(
        self,
        override: str | os.PathLike[str] | None,
    ) -> Path:
        if override is not None:
            return Path(override)
        env_override = os.getenv("OSINTAGENCY_DB_PATH")
        if env_override:
            return Path(env_override)
        return Path("data") / DEFAULT_DB_FILENAME

    def _initialize_database(self) -> SqliteDatabase:
        should_initialize = database_proxy.obj is None or PeeweeStorage._active_db_path != self.db_path
        if should_initialize:
            database = SqliteDatabase(
                self.db_path,
                pragmas={"journal_mode": "wal", "foreign_keys": 1},
            )
            database_proxy.initialize(database)
            PeeweeStorage._active_db_path = self.db_path

        database = database_proxy.obj
        database.connect(reuse_if_open=True)
        return database

    def _ensure_schema(self) -> None:
        database = database_proxy.obj
        if database is None:
            raise RuntimeError("Database has not been initialized.")
        database.create_tables([StoredMessage, DetectedVerse], safe=True)
