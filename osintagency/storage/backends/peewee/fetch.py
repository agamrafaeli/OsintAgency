"""Fetch operations for Peewee backend."""

from __future__ import annotations

import json

from peewee import fn

from osintagency.schema import DetectedVerse, ForwardedFrom, StoredMessage, Subscription

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


def fetch_analytics_summary(database) -> dict[str, object]:
    """Return aggregated analytics summary from database tables."""
    with database.connection_context():
        ensure_schema()

        # Count active subscriptions
        active_subscriptions_count = (
            Subscription.select()
            .where(Subscription.active == True)  # noqa: E712
            .count()
        )

        # Count total messages
        total_messages_count = StoredMessage.select().count()

        # Count detected verses
        detected_verses_count = DetectedVerse.select().count()

        # Get date range from messages
        date_query = StoredMessage.select(
            fn.MIN(StoredMessage.posted_at).alias("oldest"),
            fn.MAX(StoredMessage.posted_at).alias("newest"),
        ).first()

        oldest_date = date_query.oldest if date_query else None
        newest_date = date_query.newest if date_query else None

        result: dict[str, object] = {
            "active_subscriptions": active_subscriptions_count,
            "total_messages": total_messages_count,
            "detected_verses": detected_verses_count,
            "oldest_message_date": oldest_date,
            "newest_message_date": newest_date,
        }

    return result
