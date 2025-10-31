"""Business action for deterministic Telegram channel collection."""

from __future__ import annotations

import json
import os

from ..collector import (
    TelegramMessageClient,
    collect_with_stub,
    purge_database_file,
)
from ..logging_config import configure_logging, get_console_logger, get_logger
from ..storage import resolve_db_path

logger = get_logger(__name__)


def fetch_channel_action(
    *,
    limit: int,
    channel: str | None,
    db_path: str | os.PathLike[str] | None,
    cleanup: bool,
    log_level: str,
    telegram_client: TelegramMessageClient | None = None,
) -> int:
    """Persist deterministic messages or clean up the backing database."""
    configure_logging(log_level)
    console = get_console_logger()

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
            client=telegram_client,
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
        console.info(json.dumps(message, ensure_ascii=False))
    return 0


__all__ = ["fetch_channel_action"]
