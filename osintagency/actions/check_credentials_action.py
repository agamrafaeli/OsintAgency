"""Business action for validating Telegram credential configuration."""

from __future__ import annotations

import os
import sys

from ..config import ConfigurationError, TelegramConfig, load_telegram_config
from ..storage import resolve_db_path


def check_credentials_action(
    *,
    refresh_env: bool,
    generate_session: bool,
) -> int:
    """Validate environment configuration for Telegram access."""
    try:
        config = load_telegram_config(
            refresh_env=refresh_env,
            require_auth=not generate_session,
        )
    except ConfigurationError as err:
        print(f"Configuration error: {err}", file=sys.stderr)
        return 1

    db_env_raw = os.getenv("OSINTAGENCY_DB_PATH")
    db_override = db_env_raw if db_env_raw else None
    db_path = resolve_db_path(db_override)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        print(f"Database path {db_path} is not usable: {err}", file=sys.stderr)
        return 1

    if generate_session:
        session = _generate_session_string(config)
        if session is None:
            return 1
        print("Generated TELEGRAM_SESSION_STRING value:")
        print(session)
        return 0

    print("Credential check succeeded.")
    print(f"Authentication mode: {config.auth_mode}")
    print(f"Target channel id: {config.target_channel}")
    if db_override:
        print(f"OSINTAGENCY_DB_PATH override: {db_path}")
    else:
        print(f"Using default database path: {db_path}")
    return 0


def _generate_session_string(config: TelegramConfig) -> str | None:
    """Interactively collect a Telethon session string."""
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
        "Starting interactive Telethon login. You will be prompted for phone and login codes.",
    )
    try:
        with TelegramClient(StringSession(), config.api_id, config.api_hash) as client:
            client.start()
            return client.session.save()
    except Exception as err:  # noqa: BLE001 - surface all Telethon errors for debugging
        print(f"Failed to generate session string: {err}", file=sys.stderr)
        return None


__all__ = ["check_credentials_action"]
