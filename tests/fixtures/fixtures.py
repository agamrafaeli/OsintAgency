"""Pytest fixtures for storage layer testing."""

from __future__ import annotations

import pytest


@pytest.fixture
def memory_db(tmp_path):
    """
    Provide a temporary SQLite database for testing.

    This uses a temporary file that is automatically cleaned up after the test.
    Faster than persistent file-based storage and provides full isolation.

    Example:
        def test_something(memory_db):
            storage.persist_messages("@channel", [...], db_path=memory_db)
    """
    # Use tmp_path to create a temporary database file
    # This is cleaned up automatically by pytest
    db_path = tmp_path / "test.db"
    yield db_path


@pytest.fixture
def populated_db(memory_db):
    """
    Provide a temporary database pre-populated with test data.

    This fixture builds on memory_db and adds common test data
    that multiple tests can use.

    Example:
        def test_fetch(populated_db):
            rows = storage.fetch_messages("@test_channel", db_path=populated_db)
            assert len(rows) > 0
    """
    from osintagency import storage

    # Add test messages
    test_messages = [
        {"id": 1, "timestamp": "2024-01-01T10:00:00", "text": "First message"},
        {"id": 2, "timestamp": "2024-01-01T11:00:00", "text": "Second message"},
        {"id": 3, "timestamp": "2024-01-01T12:00:00", "text": "Third message"},
    ]

    storage.persist_messages("@test_channel", test_messages, db_path=memory_db)

    # Add more test data for other channels
    storage.persist_messages(
        "@another_channel",
        [{"id": 100, "timestamp": "2024-01-02T10:00:00", "text": "Another channel msg"}],
        db_path=memory_db
    )

    return memory_db


@pytest.fixture
def db_factory(tmp_path):
    """
    Factory fixture for creating multiple isolated temporary databases.

    Use this when you need multiple databases in a single test,
    or when you want to test database migration/recreation scenarios.

    Example:
        def test_multiple_dbs(db_factory):
            db1 = db_factory()
            db2 = db_factory()
            storage.persist_messages("@ch1", [...], db_path=db1)
            storage.persist_messages("@ch2", [...], db_path=db2)
    """
    counter = 0

    def _create_db():
        nonlocal counter
        counter += 1
        db_path = tmp_path / f"test_{counter}.db"
        return db_path

    yield _create_db
