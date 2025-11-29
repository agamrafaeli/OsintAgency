from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping

from peewee import EXCLUDED, SqliteDatabase, fn

from osintagency.schema import (
    DetectedVerse,
    ForwardedFrom,
    StoredMessage,
    database_proxy,
)
from osintagency.storage.interface import StorageBackend
from osintagency.storage.normalization import (
    json_default,
    normalize_detected_verses,
    normalize_message,
)
from osintagency.storage.utils import initialize_database, resolve_db_path


class PeeweeStorage(StorageBackend):
    """Peewee-backed persistence for raw Telegram messages."""


    def __init__(self, db_path: str | os.PathLike[str] | None = None):
        self.db_path = resolve_db_path(db_path)

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

        database = initialize_database(self.db_path)

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
        database = initialize_database(self.db_path)
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
        database = initialize_database(self.db_path)

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

    def persist_forwarded_channels(
        self,
        forwarded_channels: Iterable[Mapping[str, object]],
        *,
        message_ids: Iterable[int | str] | None = None,
    ) -> int:
        """Upsert forwarded channel reference rows independently from message storage."""
        database = initialize_database(self.db_path)

        # Convert to list and extract message_ids for deletion
        forwarded_list = list(forwarded_channels)
        refresh_ids: set[int] = set()

        # Add explicit message_ids for deletion
        if message_ids is not None:
            for msg_id in message_ids:
                try:
                    refresh_ids.add(int(msg_id))
                except (TypeError, ValueError):
                    pass

        # Add message_ids from the forwarded_channels data
        for item in forwarded_list:
            msg_id = item.get("message_id")
            if msg_id is not None:
                try:
                    refresh_ids.add(int(msg_id))
                except (TypeError, ValueError):
                    pass

        # Normalize rows for insertion
        normalized_rows = []
        for item in forwarded_list:
            try:
                normalized_rows.append(
                    {
                        "message_id": int(item["message_id"]),
                        "source_channel_id": item.get("source_channel_id"),
                        "source_message_id": item.get("source_message_id"),
                        "detected_at": item.get("detected_at", ""),
                    }
                )
            except (KeyError, TypeError, ValueError):
                # Skip malformed rows
                continue

        if not refresh_ids and not normalized_rows:
            self._ensure_schema()
            database.close()
            return 0

        with database.atomic():
            self._ensure_schema()
            if refresh_ids:
                (
                    ForwardedFrom.delete()
                    .where(ForwardedFrom.message_id.in_(refresh_ids))
                    .execute()
                )
            if normalized_rows:
                ForwardedFrom.insert_many(normalized_rows).execute()

        database.close()
        return len(normalized_rows)

    def fetch_forwarded_channels(self) -> list[dict[str, object]]:
        """Return aggregated channel references sorted by frequency (reference count descending)."""
        database = initialize_database(self.db_path)
        with database.connection_context():
            self._ensure_schema()
            query = (
                ForwardedFrom.select(
                    ForwardedFrom.source_channel_id,
                    fn.COUNT(ForwardedFrom.id).alias("reference_count"),
                )
                .where(ForwardedFrom.source_channel_id.is_null(False))
                .group_by(ForwardedFrom.source_channel_id)
                .order_by(fn.COUNT(ForwardedFrom.id).desc())
            )
            results: list[dict[str, object]] = [
                {
                    "source_channel_id": record.source_channel_id,
                    "reference_count": record.reference_count,
                }
                for record in query
            ]
        database.close()
        return results

    def _ensure_schema(self) -> None:
        database = database_proxy.obj
        if database is None:
            raise RuntimeError("Database has not been initialized.")
        database.create_tables(
            [StoredMessage, DetectedVerse, ForwardedFrom], safe=True
        )
