#!/usr/bin/env python3
"""Credential smoke test for Telegram access."""

from __future__ import annotations

import argparse
import sys

from osintagency.config import ConfigurationError, load_telegram_config


def _generate_session_string(config):
    if config.session_string:
        print(
            "Existing TELEGRAM_SESSION_STRING detected; generating a new one anyway.",
            file=sys.stderr,
        )
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError:
        print("Telethon must be installed to generate a session string.", file=sys.stderr)
        return None

    print(
        "Starting interactive Telethon login. You will be prompted for phone and login codes."
    )
    try:
        with TelegramClient(StringSession(), config.api_id, config.api_hash) as client:
            client.start()
            return client.session.save()
    except Exception as err:  # noqa: BLE001 - surface all Telethon errors to the console
        print(f"Failed to generate session string: {err}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Telegram credential environment variables."
    )
    parser.add_argument(
        "--refresh-env",
        action="store_true",
        help="Reload values from the .env file instead of using cached values.",
    )
    parser.add_argument(
        "--generate-session",
        action="store_true",
        help=(
            "Interactively generate a TELEGRAM_SESSION_STRING using the App API. "
            "Requires TELEGRAM_API_ID and TELEGRAM_API_HASH to be configured."
        ),
    )
    args = parser.parse_args()

    try:
        config = load_telegram_config(
            refresh_env=args.refresh_env, require_auth=not args.generate_session
        )
    except ConfigurationError as err:
        print(f"Configuration error: {err}", file=sys.stderr)
        return 1

    if args.generate_session:
        session = _generate_session_string(config)
        if session is None:
            return 1
        print("Generated TELEGRAM_SESSION_STRING value:")
        print(session)
        return 0

    print("Credential check succeeded.")
    print(f"Authentication mode: {config.auth_mode}")
    print(f"Target channel id: {config.target_channel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
