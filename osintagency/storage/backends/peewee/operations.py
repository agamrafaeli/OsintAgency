"""Database operations and schema management for Peewee backend."""

from __future__ import annotations

import os
from pathlib import Path

from osintagency.schema import (
    DetectedVerse,
    ForwardedFrom,
    StoredMessage,
    database_proxy,
)
from osintagency.storage.utils import initialize_database, resolve_db_path


def ensure_schema() -> None:
    """Create tables if they don't exist."""
    database = database_proxy.obj
    if database is None:
        raise RuntimeError("Database has not been initialized.")
    database.create_tables(
        [StoredMessage, DetectedVerse, ForwardedFrom], safe=True
    )


def get_database(db_path: str | os.PathLike[str] | None = None):
    """Initialize and return a database instance."""
    resolved_path = resolve_db_path(db_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return initialize_database(resolved_path)
