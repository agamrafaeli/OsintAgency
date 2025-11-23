from datetime import datetime, timezone

from peewee import JOIN

from osintagency import storage
from osintagency.schema import DetectedVerse, StoredMessage


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


def test_persist_messages_serializes_datetime_payload(tmp_path):
    db_path = tmp_path / "messages.sqlite"
    message = {
        "id": 1,
        "timestamp": "2024-01-03T00:00:00",
        "text": "live message",
        "fetched_at": datetime(2024, 1, 3, 12, 30, tzinfo=timezone.utc),
    }

    storage.persist_messages("@channel", [message], db_path=db_path)
    rows = storage.fetch_messages("@channel", db_path=db_path)

    assert rows[0]["raw_payload"]["fetched_at"] == message["fetched_at"].isoformat()


def test_detected_verse_rows_persist_with_join(tmp_path):
    db_path = tmp_path / "messages.sqlite"
    message_payload = {
        "id": 42,
        "timestamp": "2024-04-20T12:00:00",
        "text": "Reference to 2:255 and 2:256.",
    }

    storage.persist_messages("@analysis", [message_payload], db_path=db_path)

    database = storage._initialize_database(db_path)
    try:
        storage._ensure_schema()
        with database.atomic():
            DetectedVerse.insert_many(
                [
                    {
                        "message_id": 42,
                        "sura": 2,
                        "ayah": 255,
                        "confidence": 0.95,
                        "is_partial": False,
                    },
                    {
                        "message_id": 42,
                        "sura": 2,
                        "ayah": 256,
                        "confidence": 0.7,
                        "is_partial": True,
                    },
                ]
            ).execute()
    finally:
        database.close()

    database = storage._initialize_database(db_path)
    try:
        joined_rows = list(
            StoredMessage.select(
                StoredMessage.channel_id,
                StoredMessage.message_id,
                DetectedVerse.sura,
                DetectedVerse.ayah,
                DetectedVerse.confidence,
                DetectedVerse.is_partial,
            )
            .join(
                DetectedVerse,
                JOIN.INNER,
                on=(DetectedVerse.message_id == StoredMessage.message_id),
            )
            .where(StoredMessage.message_id == 42)
            .order_by(DetectedVerse.id)
            .dicts()
        )
    finally:
        database.close()

    assert [row["channel_id"] for row in joined_rows] == ["@analysis", "@analysis"]
    assert [(row["sura"], row["ayah"]) for row in joined_rows] == [(2, 255), (2, 256)]
    assert joined_rows[0]["confidence"] == 0.95
    assert joined_rows[1]["is_partial"] is True


def test_persist_detected_verses_inserts_rows(tmp_path):
    db_path = tmp_path / "messages.sqlite"
    message_payload = {
        "id": 7,
        "timestamp": "2024-04-01T00:00:00",
        "text": "Reference to ayat",
    }

    storage.persist_messages("@analysis", [message_payload], db_path=db_path)

    inserted = storage.persist_detected_verses(
        [
            {
                "message_id": 7,
                "sura": 1,
                "ayah": 2,
                "confidence": 0.88,
                "is_partial": True,
            }
        ],
        message_ids=[7],
        db_path=db_path,
    )
    assert inserted == 1

    database = storage._initialize_database(db_path)
    try:
        storage._ensure_schema()
        verse_rows = list(DetectedVerse.select().dicts())
    finally:
        database.close()

    assert len(verse_rows) == 1
    assert verse_rows[0]["message_id"] == 7
    assert verse_rows[0]["sura"] == 1
    assert verse_rows[0]["ayah"] == 2
    assert verse_rows[0]["is_partial"] is True


def test_persist_detected_verses_refreshes_rows(tmp_path):
    db_path = tmp_path / "messages.sqlite"
    payload = {
        "id": 99,
        "timestamp": "2024-04-02T00:00:00",
        "text": "First revision",
    }

    storage.persist_messages("@analysis", [payload], db_path=db_path)

    storage.persist_detected_verses(
        [
            {
                "message_id": 99,
                "sura": 2,
                "ayah": 255,
                "confidence": 1.0,
                "is_partial": False,
            }
        ],
        message_ids=[99],
        db_path=db_path,
    )

    storage.persist_detected_verses(
        [],
        message_ids=[99],
        db_path=db_path,
    )

    database = storage._initialize_database(db_path)
    try:
        storage._ensure_schema()
        assert DetectedVerse.select().count() == 0
    finally:
        database.close()
