from osintagency import storage


def test_persist_messages_creates_table_and_upserts(tmp_path):
    db_path = tmp_path / "messages.sqlite"
    first_batch = [
        {"id": 1, "timestamp": "2024-01-01T00:00:00", "text": "hello"},
    ]
    second_batch = [
        {"id": 1, "timestamp": "2024-01-02T00:00:00", "text": "updated"},
        {"id": 2, "timestamp": "2024-01-02T00:05:00", "text": "world"},
    ]

    storage.persist_messages("@channel", first_batch, db_path=db_path)
    storage.persist_messages("@channel", second_batch, db_path=db_path)

    rows = storage.fetch_messages("@channel", db_path=db_path)
    assert [row["message_id"] for row in rows] == [1, 2]
    first_row = rows[0]
    assert first_row["channel_id"] == "@channel"
    assert first_row["posted_at"] == "2024-01-02T00:00:00"
    assert first_row["text"] == "updated"
    assert first_row["raw_payload"]["text"] == "updated"


def test_persist_messages_handles_empty_batch(tmp_path):
    db_path = tmp_path / "messages.sqlite"

    storage.persist_messages("@channel", [], db_path=db_path)

    rows = storage.fetch_messages("@channel", db_path=db_path)
    assert rows == []
