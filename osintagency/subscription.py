"""Subscription management for Telegram channels."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from peewee import EXCLUDED

from .schema import Subscription, database_proxy
from .storage import initialize_database, resolve_db_path


def add_subscription(
    channel_id: str,
    *,
    name: str | None = None,
    metadata: dict | None = None,
    db_path: str | os.PathLike[str] | None = None,
) -> bool:
    """
    Add or update a channel subscription.

    Args:
        channel_id: The Telegram channel identifier (e.g., "@channel" or numeric ID)
        name: Human-readable channel name
        metadata: Optional metadata dictionary
        db_path: Database file path (defaults to configured path)

    Returns:
        True if subscription was added/updated successfully
    """
    target_path = resolve_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    database = initialize_database(target_path)

    # Prepare subscription data
    added_at = datetime.now(timezone.utc).isoformat()
    metadata_json = json.dumps(metadata) if metadata else None

    subscription_data = {
        "channel_id": channel_id,
        "name": name,
        "added_at": added_at,
        "active": True,
        "metadata": metadata_json,
    }

    with database.atomic():
        _ensure_schema()
        # Upsert: insert or update if exists
        Subscription.insert(subscription_data).on_conflict(
            conflict_target=[Subscription.channel_id],
            update={
                Subscription.name: EXCLUDED.name,
                Subscription.added_at: EXCLUDED.added_at,
                Subscription.active: EXCLUDED.active,
                Subscription.metadata: EXCLUDED.metadata,
            },
        ).execute()

    database.close()
    return True


def get_subscriptions(
    *,
    active_only: bool = True,
    db_path: str | os.PathLike[str] | None = None,
) -> list[dict[str, object]]:
    """
    Retrieve stored subscriptions.

    Args:
        active_only: If True, return only active subscriptions
        db_path: Database file path (defaults to configured path)

    Returns:
        List of subscription dictionaries
    """
    target_path = resolve_db_path(db_path)
    database = initialize_database(target_path)

    with database.connection_context():
        _ensure_schema()
        query = Subscription.select()
        if active_only:
            query = query.where(Subscription.active == True)  # noqa: E712

        results: list[dict[str, object]] = [
            {
                "channel_id": record.channel_id,
                "name": record.name,
                "added_at": record.added_at,
                "active": bool(record.active),
                "metadata": json.loads(record.metadata) if record.metadata else None,
            }
            for record in query
        ]

    database.close()
    return results


def update_subscription(
    channel_id: str,
    *,
    name: str | None = None,
    active: bool | None = None,
    metadata: dict | None = None,
    db_path: str | os.PathLike[str] | None = None,
) -> bool:
    """
    Update an existing subscription.

    Args:
        channel_id: The Telegram channel identifier
        name: New channel name (optional)
        active: New active status (optional)
        metadata: New metadata (optional)
        db_path: Database file path (defaults to configured path)

    Returns:
        True if subscription was updated, False if not found
    """
    target_path = resolve_db_path(db_path)
    database = initialize_database(target_path)

    with database.atomic():
        _ensure_schema()
        query = Subscription.update()

        # Build update dict with only provided fields
        update_data = {}
        if name is not None:
            update_data[Subscription.name] = name
        if active is not None:
            update_data[Subscription.active] = active
        if metadata is not None:
            update_data[Subscription.metadata] = json.dumps(metadata)

        if not update_data:
            database.close()
            return False

        rows_updated = (
            query.where(Subscription.channel_id == channel_id)
            .execute()
            if not update_data
            else Subscription.update(update_data)
            .where(Subscription.channel_id == channel_id)
            .execute()
        )

    database.close()
    return rows_updated > 0


def remove_subscription(
    channel_id: str,
    *,
    db_path: str | os.PathLike[str] | None = None,
) -> bool:
    """
    Remove a subscription.

    Args:
        channel_id: The Telegram channel identifier
        db_path: Database file path (defaults to configured path)

    Returns:
        True if subscription was removed, False if not found
    """
    target_path = resolve_db_path(db_path)
    database = initialize_database(target_path)

    with database.atomic():
        _ensure_schema()
        rows_deleted = (
            Subscription.delete().where(Subscription.channel_id == channel_id).execute()
        )

    database.close()
    return rows_deleted > 0


def _ensure_schema() -> None:
    """Ensure the subscriptions table exists."""
    database = database_proxy.obj
    if database is None:
        raise RuntimeError("Database has not been initialized.")
    database.create_tables([Subscription], safe=True)
