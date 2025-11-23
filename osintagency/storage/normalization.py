from __future__ import annotations

import json
from datetime import date, datetime
from typing import Iterable, Mapping, MutableMapping

def normalize_message(message: Mapping[str, object]) -> MutableMapping[str, object]:
    """Normalize a raw message payload into a standard format."""
    if "id" not in message:
        raise ValueError("Message payload missing 'id' field.")

    normalized: MutableMapping[str, object] = {
        "message_id": message["id"],
        "posted_at": message.get("timestamp"),
        "text": message.get("text", "") or "",
        "raw_payload": dict(message),
    }
    try:
        normalized["message_id"] = int(normalized["message_id"])
    except (TypeError, ValueError) as err:
        raise ValueError("Message 'id' must be an integer.") from err

    posted_at = normalized["posted_at"]
    if posted_at is not None and not isinstance(posted_at, str):
        normalized["posted_at"] = str(posted_at)

    text = normalized["text"]
    if not isinstance(text, str):
        normalized["text"] = str(text) if text is not None else ""

    return normalized

def normalize_detected_verses(
    detected_verses: Iterable[Mapping[str, object]],
    message_ids: Iterable[int | str] | None,
) -> tuple[list[dict[str, object]], set[int]]:
    """Normalize detected verse rows and identify message IDs to refresh."""
    refresh_ids: set[int] = set()
    if message_ids is not None:
        for identifier in message_ids:
            try:
                refresh_ids.add(int(identifier))
            except (TypeError, ValueError):
                continue

    normalized_rows: list[dict[str, object]] = []
    seen_rows: set[tuple[int, int, int]] = set()

    for row in detected_verses:
        try:
            message_id = int(row["message_id"])
            sura = int(row["sura"])
            ayah = int(row["ayah"])
        except (KeyError, TypeError, ValueError):
            continue

        if message_ids is not None and message_id not in refresh_ids:
            continue

        refresh_ids.add(message_id)
        confidence = float(row.get("confidence", 1.0))
        is_partial = bool(row.get("is_partial", False))
        key = (message_id, sura, ayah)
        if key in seen_rows:
            continue
        seen_rows.add(key)
        normalized_rows.append(
            {
                "message_id": message_id,
                "sura": sura,
                "ayah": ayah,
                "confidence": confidence,
                "is_partial": is_partial,
            }
        )

    if message_ids is None and not refresh_ids:
        refresh_ids.update(row["message_id"] for row in normalized_rows)

    return normalized_rows, refresh_ids

def json_default(value: object) -> str:
    """JSON serializer for objects not serializable by default json code."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)
