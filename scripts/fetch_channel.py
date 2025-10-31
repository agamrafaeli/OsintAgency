#!/usr/bin/env python3
"""Fetch recent posts from a Telegram channel."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from typing import Any, Dict, List

from osintagency.config import ConfigurationError, load_telegram_config


logger = logging.getLogger(__name__)


def _load_telethon():
    from telethon import TelegramClient
    from telethon.errors import RPCError
    from telethon.sessions import StringSession

    return TelegramClient, StringSession, RPCError


async def _create_client(config):
    TelegramClient, StringSession, _ = _load_telethon()
    if config.session_string:
        session = StringSession(config.session_string)
        client = TelegramClient(session, config.api_id, config.api_hash)
        await client.connect()
    else:
        # Fall back to bot credential mode when a session string is not provided.
        client = TelegramClient("bot", config.api_id, config.api_hash)
        await client.start(bot_token=config.bot_token)
    return client


async def _fetch_messages(client, channel: str, limit: int) -> List[Dict[str, Any]]:
    entity = await client.get_entity(channel)
    messages: List[Dict[str, Any]] = []

    async for message in client.iter_messages(entity, limit=limit):
        messages.append(
            {
                "id": message.id,
                "timestamp": message.date.isoformat() if message.date else None,
                "text": (message.message or "").strip(),
            }
        )
    return messages


async def async_main(args) -> int:
    try:
        config = load_telegram_config()
    except ConfigurationError as err:
        logger.error("Configuration error: %s", err)
        return 1

    if args.channel:
        target_channel = args.channel
    else:
        target_channel = config.target_channel

    client = await _create_client(config)
    _, _, RPCError = _load_telethon()
    try:
        messages = await _fetch_messages(client, target_channel, limit=args.limit)
    except RPCError as err:
        logger.error("Telegram API error: %s", err)
        return 1
    finally:
        await client.disconnect()

    if not messages:
        logger.warning("No messages returned for %s", target_channel)

    for message in messages:
        print(json.dumps(message, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download recent posts from a Telegram channel."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of recent posts to retrieve (default: 5).",
    )
    parser.add_argument(
        "--channel",
        help="Override the target channel id or username defined in the environment.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        help="Python logging level (default: WARNING).",
    )
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.WARNING))

    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
