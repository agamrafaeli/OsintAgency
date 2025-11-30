"""Business action for Telegram channel collection."""

from __future__ import annotations

from datetime import datetime
import json
import os

from ..clients import TelegramMessageClient
from ..collector import collect_messages
from ..config import ConfigurationError
from ..logging_config import configure_logging, get_console_logger, get_logger

logger = get_logger(__name__)


def fetch_channel_action(
    *,
    limit: int,
    channel_id: str | None,
    db_path: str | os.PathLike[str] | None,
    log_level: str,
    telegram_client: TelegramMessageClient | None = None,
    offset_date: datetime | None = None,
) -> int:
    """Persist Telegram messages from Telegram into storage."""
    configure_logging(log_level)
    console = get_console_logger()

    if telegram_client is None:
        console.error("No telegram client provided for collection.")
        return 1

    try:
        outcome = collect_messages(
            limit=limit,
            channel_id=channel_id,
            db_path=db_path,
            telegram_client=telegram_client,
            offset_date=offset_date,
        )
    except ConfigurationError as err:
        console.error("Configuration error: %s", err)
        return 1
    except RuntimeError as err:
        console.error("Channel collection failed: %s", err)
        logger.exception("Channel collection failed.")
        return 1
    except Exception:  # noqa: BLE001 - surfaced to the console for debugging
        logger.exception("Channel collection failed.")
        return 1

    logger.info(
        "Persisted %d message(s) for %s at %s",
        outcome.stored_messages,
        outcome.channel_id,
        outcome.db_path,
    )
    for message in outcome.messages:
        console.info(json.dumps(message, ensure_ascii=False, default=str))
    return 0


__all__ = ["fetch_channel_action"]
