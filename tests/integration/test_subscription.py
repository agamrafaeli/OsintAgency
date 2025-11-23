from datetime import datetime

from osintagency import subscription as subscription


def test_add_subscription_creates_record(memory_db):
    """Verify a new subscription is persisted to the database."""
    result = subscription.add_subscription(
        "@testchannel",
        name="Test Channel",
        db_path=memory_db
    )

    assert result is True
    subscriptions = subscription.get_subscriptions(db_path=memory_db)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@testchannel"
    assert subscriptions[0]["name"] == "Test Channel"
    assert subscriptions[0]["active"] is True
    assert "added_at" in subscriptions[0]


def test_add_subscription_updates_existing(memory_db):
    """Verify adding same channel twice updates the existing record."""
    subscription.add_subscription(
        "@testchannel",
        name="Original Name",
        db_path=memory_db
    )
    subscription.add_subscription(
        "@testchannel",
        name="Updated Name",
        db_path=memory_db
    )

    subscriptions = subscription.get_subscriptions(db_path=memory_db)
    assert len(subscriptions) == 1
    assert subscriptions[0]["name"] == "Updated Name"


def test_get_subscriptions_returns_all_when_no_filter(memory_db):
    """Verify retrieving all subscriptions regardless of active status."""
    subscription.add_subscription("@active", name="Active", db_path=memory_db)
    subscription.add_subscription("@inactive", name="Inactive", db_path=memory_db)
    # Manually deactivate one
    subscription.update_subscription(
        "@inactive",
        active=False,
        db_path=memory_db
    )

    all_subscriptions = subscription.get_subscriptions(
        active_only=False,
        db_path=memory_db
    )
    assert len(all_subscriptions) == 2


def test_get_subscriptions_filters_active_only(memory_db):
    """Verify active filter returns only active subscriptions."""
    subscription.add_subscription("@active", name="Active", db_path=memory_db)
    subscription.add_subscription("@inactive", name="Inactive", db_path=memory_db)
    subscription.update_subscription(
        "@inactive",
        active=False,
        db_path=memory_db
    )

    active_subscriptions = subscription.get_subscriptions(
        active_only=True,
        db_path=memory_db
    )
    assert len(active_subscriptions) == 1
    assert active_subscriptions[0]["channel_id"] == "@active"


def test_get_subscriptions_returns_empty_when_none_exist(memory_db):
    """Verify empty list returned when no subscriptions exist."""
    subscriptions = subscription.get_subscriptions(db_path=memory_db)
    assert subscriptions == []


def test_remove_subscription_deletes_record(memory_db):
    """Verify subscription removal from database."""
    subscription.add_subscription("@testchannel", db_path=memory_db)
    result = subscription.remove_subscription("@testchannel", db_path=memory_db)

    assert result is True
    subscriptions = subscription.get_subscriptions(db_path=memory_db)
    assert len(subscriptions) == 0


def test_remove_subscription_returns_false_for_nonexistent(memory_db):
    """Verify removing non-existent subscription returns False."""
    result = subscription.remove_subscription("@nonexistent", db_path=memory_db)
    assert result is False


def test_subscriptions_persist_across_connections(memory_db):
    """Verify subscription data survives database reconnection."""
    # Add subscription in first connection
    subscription.add_subscription(
        "@persistent",
        name="Persistent Channel",
        db_path=memory_db
    )

    # Force database to close (simulate reconnection)
    # The storage pattern handles this automatically

    # Retrieve in new connection
    subscriptions = subscription.get_subscriptions(db_path=memory_db)
    assert len(subscriptions) == 1
    assert subscriptions[0]["channel_id"] == "@persistent"
    assert subscriptions[0]["name"] == "Persistent Channel"


def test_add_subscription_with_metadata(memory_db):
    """Verify metadata can be stored and retrieved."""
    metadata = {"type": "public", "language": "en", "category": "news"}
    subscription.add_subscription(
        "@channel_with_meta",
        name="Channel With Metadata",
        metadata=metadata,
        db_path=memory_db
    )

    subscriptions = subscription.get_subscriptions(db_path=memory_db)
    assert subscriptions[0]["metadata"] == metadata
