"""Peewee-backed storage implementation."""

from __future__ import annotations

import os
from typing import Iterable, Mapping

from osintagency.storage.interface import StorageBackend
from osintagency.storage.utils import resolve_db_path

from . import fetch, operations, persistence


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
        database = operations.get_database(self.db_path)
        try:
            count = persistence.persist_messages(database, channel_id, messages)
            return count
        finally:
            database.close()

    def fetch_messages(
        self,
        channel_id: str | None = None,
    ) -> list[dict[str, object]]:
        """Return stored messages ordered by message id for verification and analytics."""
        database = operations.get_database(self.db_path)
        try:
            results = fetch.fetch_messages(database, channel_id)
            return results
        finally:
            database.close()

    def persist_detected_verses(
        self,
        detected_verses: Iterable[Mapping[str, object]],
        *,
        message_ids: Iterable[int | str] | None = None,
    ) -> int:
        """Upsert detected verse rows independently from message storage."""
        database = operations.get_database(self.db_path)
        try:
            count = persistence.persist_detected_verses(
                database, detected_verses, message_ids=message_ids
            )
            return count
        finally:
            database.close()

    def persist_forwarded_channels(
        self,
        forwarded_channels: Iterable[Mapping[str, object]],
        *,
        message_ids: Iterable[int | str] | None = None,
    ) -> int:
        """Upsert forwarded channel reference rows independently from message storage."""
        database = operations.get_database(self.db_path)
        try:
            count = persistence.persist_forwarded_channels(
                database, forwarded_channels, message_ids=message_ids
            )
            return count
        finally:
            database.close()

    def fetch_forwarded_channels(self) -> list[dict[str, object]]:
        """Return aggregated channel references sorted by frequency (reference count descending)."""
        database = operations.get_database(self.db_path)
        try:
            results = fetch.fetch_forwarded_channels(database)
            return results
        finally:
            database.close()

    def _ensure_schema(self) -> None:
        """Create tables if they don't exist (for backward compatibility)."""
        operations.ensure_schema()
