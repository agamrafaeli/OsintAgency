from typing import Iterable, Mapping
import os

from .factory import get_storage_backend

# Facade functions to maintain backward compatibility

def persist_messages(
    channel_id: str,
    messages: Iterable[Mapping[str, object]],
    *,
    db_path: str | os.PathLike[str] | None = None,
) -> int:
    """Upsert message records into the raw message store."""
    backend = get_storage_backend(db_path=db_path)
    return backend.persist_messages(channel_id, messages)

def fetch_messages(
    channel_id: str | None = None,
    *,
    db_path: str | os.PathLike[str] | None = None,
) -> list[dict[str, object]]:
    """Return stored messages ordered by message id for verification and analytics."""
    backend = get_storage_backend(db_path=db_path)
    return backend.fetch_messages(channel_id)

def persist_detected_verses(
    detected_verses: Iterable[Mapping[str, object]],
    *,
    message_ids: Iterable[int | str] | None = None,
    db_path: str | os.PathLike[str] | None = None,
) -> int:
    """Upsert detected verse rows independently from message storage."""
    backend = get_storage_backend(db_path=db_path)
    return backend.persist_detected_verses(detected_verses, message_ids=message_ids)
