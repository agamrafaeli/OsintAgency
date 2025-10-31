"""Business action for fetching all subscribed channels."""

from __future__ import annotations

import os
from dataclasses import dataclass

from ..collector import TelegramMessageClient, collect_messages
from ..config import ConfigurationError
from ..logging_config import configure_logging, get_console_logger, get_logger
from ..subscription import get_subscriptions

logger = get_logger(__name__)


@dataclass
class FetchResult:
    """Result of fetching from a single channel."""

    channel_id: str
    success: bool
    message_count: int


def _fetch_from_channel(
    subscription: dict,
    limit: int,
    db_path: str | os.PathLike[str] | None,
    telegram_client: TelegramMessageClient,
) -> FetchResult:
    """Fetch messages from a single subscribed channel."""
    console = get_console_logger()
    channel_id = subscription["channel_id"]
    channel_name = subscription.get("name") or channel_id

    try:
        console.info("Fetching messages from %s (%s)...", channel_name, channel_id)
        outcome = collect_messages(
            limit=limit,
            channel_id=channel_id,
            db_path=db_path,
            telegram_client=telegram_client,
        )
        console.info("Stored %d message(s) from %s", outcome.stored_messages, channel_id)
        return FetchResult(channel_id, success=True, message_count=outcome.stored_messages)

    except ConfigurationError as err:
        console.error("Configuration error for %s: %s", channel_id, err)
        return FetchResult(channel_id, success=False, message_count=0)
    except RuntimeError as err:
        console.error("Failed to fetch from %s: %s", channel_id, err)
        logger.exception("Channel collection failed for %s", channel_id)
        return FetchResult(channel_id, success=False, message_count=0)
    except Exception as err:  # noqa: BLE001 - surfaced to the console for debugging
        console.error("Unexpected error for %s: %s", channel_id, err)
        logger.exception("Unexpected error collecting from %s", channel_id)
        return FetchResult(channel_id, success=False, message_count=0)


def _report_summary(results: list[FetchResult]) -> None:
    """Log summary of fetch operation."""
    console = get_console_logger()
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    total_messages = sum(r.message_count for r in results)

    console.info(
        "Completed: %d/%d channels successful, %d total messages stored",
        len(successful),
        len(results),
        total_messages,
    )

    if failed:
        console.warning("Failed channels: %s", ", ".join(r.channel_id for r in failed))


def fetch_subscriptions_action(
    *,
    limit: int,
    db_path: str | os.PathLike[str] | None,
    log_level: str,
    telegram_client: TelegramMessageClient | None = None,
) -> int:
    """Fetch messages from all active subscribed channels."""
    configure_logging(log_level)
    console = get_console_logger()

    if telegram_client is None:
        console.error("No telegram client provided for collection.")
        return 1

    try:
        subscriptions = get_subscriptions(active_only=True, db_path=db_path)

        if not subscriptions:
            console.info("No active subscriptions found.")
            return 0

        console.info("Found %d active subscription(s). Fetching messages...", len(subscriptions))

        results = [
            _fetch_from_channel(sub, limit, db_path, telegram_client)
            for sub in subscriptions
        ]

        _report_summary(results)

        return 0 if all(r.success for r in results) else 1

    except Exception:  # noqa: BLE001 - surfaced to the console for debugging
        logger.exception("Failed to fetch subscriptions.")
        return 1


__all__ = ["fetch_subscriptions_action"]
