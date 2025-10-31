from __future__ import annotations

from pathlib import Path

import pytest

from osintagency import storage


@pytest.fixture(autouse=True)
def bypass_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")


def test_stubbed_collection_respects_db_env(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_API_ID", "12345")
    monkeypatch.setenv("TELEGRAM_API_HASH", "hash")
    monkeypatch.setenv("TELEGRAM_TARGET_CHANNEL", "@sample")
    db_path = tmp_path / "custom_dir" / "messages.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))

    from osintagency.collector import (
        CollectionOutcome,
        DeterministicTelegramClient,
        collect_messages,
        purge_database_file,
    )

    outcome = collect_messages(
        limit=5,
        telegram_client=DeterministicTelegramClient(),
    )

    assert isinstance(outcome, CollectionOutcome)
    assert outcome.channel_id == "@sample"
    assert outcome.stored_messages == 5
    assert outcome.db_path == Path(db_path)
    assert db_path.exists()

    rows = storage.fetch_messages("@sample", db_path=db_path)
    assert len(rows) == 5
    assert [row["message_id"] for row in rows] == [1, 2, 3, 4, 5]

    purge_database_file(db_path=outcome.db_path)
    assert not db_path.exists()
