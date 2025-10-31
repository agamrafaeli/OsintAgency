"""Business action for deterministic Telegram channel collection."""

from __future__ import annotations

import json
import logging
import os

from ..collector import collect_with_stub, purge_database_file
from ..storage import resolve_db_path

logger = logging.getLogger(__name__)


def fetch_channel_action(
    *,
    limit: int,
    channel: str | None,
    db_path: str | os.PathLike[str] | None,
    cleanup: bool,
    log_level: str,
) -> int:
    """Persist deterministic messages or clean up the backing database."""
    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.WARNING))

    if cleanup:
        target = resolve_db_path(db_path)
        removed = purge_database_file(db_path=target)
        if removed:
            logger.info("Removed database at %s", target)
        else:
            logger.info("No database found at %s", target)
        return 0

    try:
        outcome = collect_with_stub(
            limit=limit,
            channel_override=channel,
            db_path=db_path,
        )
    except Exception:  # noqa: BLE001 - surfaced to the console for debugging
        logger.exception("Deterministic collection failed.")
        return 1

    logger.info(
        "Persisted %d message(s) for %s at %s",
        outcome.stored_messages,
        outcome.channel_id,
        outcome.db_path,
    )
    for message in outcome.messages:
        print(json.dumps(message, ensure_ascii=False))
    return 0


__all__ = ["fetch_channel_action"]
