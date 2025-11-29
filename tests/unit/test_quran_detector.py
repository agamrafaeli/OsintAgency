from osintagency import storage
from osintagency.schema import DetectedVerse
from osintagency.services import quran_detector
from osintagency.storage.utils import initialize_database


def test_detect_verses_returns_empty_when_no_quote():
    text = (
        "هذا تحليل سياسي عن أوضاع المنطقة، يذكر آراء الباحثين دون اقتباس مباشر من القرآن."
    )
    detected = quran_detector.detect_verses(message_id=5, text=text)
    assert detected == []


def test_detect_verses_finds_single_quote():
    text = "في درس التوحيد تلا المدرس قوله تعالى: قُلْ هُوَ اللَّهُ أَحَدٌ."
    detected = quran_detector.detect_verses(message_id=11, text=text)

    assert len(detected) == 1
    verse = detected[0]
    assert verse["message_id"] == 11
    assert (verse["sura"], verse["ayah"]) == (112, 1)
    assert verse["is_partial"] is False


def test_detect_verses_enriches_multiple_quotes(tmp_path):
    db_path = tmp_path / "messages.sqlite"
    text = (
        "خلال الخطبة تلا الإمام قوله تعالى: "
        "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ "
        "لَهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ "
        "ثم أشار إلى تتمة الكلام قائلاً: "
        "لَا إِكْرَاهَ فِي الدِّينِ ۖ قَدْ تَبَيَّنَ الرُّشْدُ مِنَ الْغَيِّ ۚ "
        "فَمَنْ يَكْفُرْ بِالطَّاغُوتِ وَيُؤْمِنْ بِاللَّهِ فَقَدِ اسْتَمْسَكَ بِالْعُرْوَةِ الْوُثْقَىٰ."
    )
    detected = quran_detector.detect_verses(
        message_id=77,
        text=text,
    )

    ayahs = sorted((row["sura"], row["ayah"]) for row in detected)
    assert ayahs == [(2, 255), (2, 256)]
    assert all(row["message_id"] == 77 for row in detected)
    assert all(row["is_partial"] is False for row in detected)

    storage.persist_messages(
        "@analysis",
        [{"id": 77, "timestamp": "2024-05-05T00:00:00", "text": text}],
        db_path=db_path,
    )

    database = initialize_database(db_path)
    try:
        from osintagency.storage.backends.peewee_backend import PeeweeStorage
        backend = PeeweeStorage(db_path)
        backend._ensure_schema()
        with database.atomic():
            DetectedVerse.insert_many(detected).execute()

        rows = (
            DetectedVerse.select(
                DetectedVerse.message_id,
                DetectedVerse.sura,
                DetectedVerse.ayah,
                DetectedVerse.confidence,
                DetectedVerse.is_partial,
            )
            .order_by(DetectedVerse.ayah)
            .dicts()
        )
    finally:
        database.close()

    assert [row["message_id"] for row in rows] == [77, 77]
    assert [row["is_partial"] for row in rows] == [False, False]
    assert rows[0]["confidence"] == 1.0
