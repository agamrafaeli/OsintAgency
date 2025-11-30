"""Persistence operations for Peewee backend."""

from __future__ import annotations

import json
from typing import Iterable, Mapping, MutableMapping

from peewee import EXCLUDED

from osintagency.schema import DetectedVerse, ForwardedFrom, StoredMessage
from osintagency.storage.normalization import (
    json_default,
    normalize_detected_verses,
    normalize_message,
)

from .operations import ensure_schema


def persist_messages(
    database,
    channel_id: str,
    messages: Iterable[Mapping[str, object]],
) -> int:
    """Upsert message records into the raw message store."""
    message_buffer: list[MutableMapping[str, object]] = [
        normalize_message(payload) for payload in messages
    ]

    if not message_buffer:
        ensure_schema()
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
        ensure_schema()
        StoredMessage.insert_many(serialized_messages).on_conflict(
            conflict_target=[StoredMessage.channel_id, StoredMessage.message_id],
            update={
                StoredMessage.posted_at: EXCLUDED.posted_at,
                StoredMessage.text: EXCLUDED.text,
                StoredMessage.raw_payload: EXCLUDED.raw_payload,
            },
        ).execute()

    return len(message_buffer)


def persist_detected_verses(
    database,
    detected_verses: Iterable[Mapping[str, object]],
    *,
    message_ids: Iterable[int | str] | None = None,
) -> int:
    """Upsert detected verse rows independently from message storage."""
    normalized_rows, refresh_ids = normalize_detected_verses(
        detected_verses, message_ids
    )

    if not refresh_ids and not normalized_rows:
        ensure_schema()
        return 0

    with database.atomic():
        ensure_schema()
        if refresh_ids:
            (
                DetectedVerse.delete()
                .where(DetectedVerse.message_id.in_(refresh_ids))
                .execute()
            )
        if normalized_rows:
            DetectedVerse.insert_many(normalized_rows).execute()

    return len(normalized_rows)


def persist_forwarded_channels(
    database,
    forwarded_channels: Iterable[Mapping[str, object]],
    *,
    message_ids: Iterable[int | str] | None = None,
) -> int:
    """Upsert forwarded channel reference rows independently from message storage."""
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
        ensure_schema()
        return 0

    with database.atomic():
        ensure_schema()
        if refresh_ids:
            (
                ForwardedFrom.delete()
                .where(ForwardedFrom.message_id.in_(refresh_ids))
                .execute()
            )
        if normalized_rows:
            ForwardedFrom.insert_many(normalized_rows).execute()

    return len(normalized_rows)
