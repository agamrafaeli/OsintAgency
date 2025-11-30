"""Fetch operations for Peewee backend."""

from __future__ import annotations

import json

from peewee import fn

from osintagency.schema import ForwardedFrom, StoredMessage

from .operations import ensure_schema


def fetch_messages(
    database,
    channel_id: str | None = None,
) -> list[dict[str, object]]:
    """Return stored messages ordered by message id for verification and analytics."""
    with database.connection_context():
        ensure_schema()
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
    return results


def fetch_forwarded_channels(database) -> list[dict[str, object]]:
    """Return aggregated channel references sorted by frequency (reference count descending)."""
    with database.connection_context():
        ensure_schema()
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
    return results
