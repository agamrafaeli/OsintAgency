import os
from pathlib import Path

from peewee import SqliteDatabase
from osintagency.schema import database_proxy

DEFAULT_DB_FILENAME = "messages.sqlite3"
_active_db_path: Path | None = None

def resolve_db_path(
    override: str | os.PathLike[str] | None = None,
) -> Path:
    """Resolve the database path from override, environment, or default."""
    if override is not None:
        return Path(override)
    env_override = os.getenv("OSINTAGENCY_DB_PATH")
    if env_override:
        return Path(env_override)
    return Path("data") / DEFAULT_DB_FILENAME

def initialize_database(db_path: Path) -> SqliteDatabase:
    """Initialize the Peewee database proxy."""
    global _active_db_path
    should_initialize = database_proxy.obj is None or _active_db_path != db_path
    if should_initialize:
        database = SqliteDatabase(
            db_path,
            pragmas={"journal_mode": "wal", "foreign_keys": 1},
        )
        database_proxy.initialize(database)
        _active_db_path = db_path

    database = database_proxy.obj
    database.connect(reuse_if_open=True)
    return database
