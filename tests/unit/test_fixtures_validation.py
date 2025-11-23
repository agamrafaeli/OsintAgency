"""Validation tests for storage fixtures."""

from osintagency import storage


def test_memory_db_fixture_works(memory_db):
    """Verify memory_db fixture provides working database."""
    # Should be able to persist and fetch messages
    messages = [
        {"id": 1, "timestamp": "2024-01-01T10:00:00", "text": "test message"}
    ]

    count = storage.persist_messages("@testchannel", messages, db_path=memory_db)
    assert count == 1

    rows = storage.fetch_messages("@testchannel", db_path=memory_db)
    assert len(rows) == 1
    assert rows[0]["text"] == "test message"


def test_populated_db_fixture_has_data(populated_db):
    """Verify populated_db fixture comes with test data."""
    rows = storage.fetch_messages("@test_channel", db_path=populated_db)
    assert len(rows) == 3
    assert rows[0]["text"] == "First message"

    rows = storage.fetch_messages("@another_channel", db_path=populated_db)
    assert len(rows) == 1
    assert rows[0]["text"] == "Another channel msg"


def test_db_factory_creates_isolated_databases(db_factory):
    """Verify db_factory creates independent database instances."""
    db1 = db_factory()
    db2 = db_factory()

    # Add data to db1
    storage.persist_messages(
        "@channel1",
        [{"id": 1, "timestamp": "2024-01-01T10:00:00", "text": "db1 message"}],
        db_path=db1
    )

    # Add data to db2
    storage.persist_messages(
        "@channel2",
        [{"id": 2, "timestamp": "2024-01-01T11:00:00", "text": "db2 message"}],
        db_path=db2
    )

    # Verify isolation - db1 should not have db2's data
    rows1 = storage.fetch_messages(db_path=db1)
    rows2 = storage.fetch_messages(db_path=db2)

    assert len(rows1) == 1
    assert rows1[0]["text"] == "db1 message"

    assert len(rows2) == 1
    assert rows2[0]["text"] == "db2 message"
