"""Business action for validating Telegram credential configuration."""

from __future__ import annotations

import os

from ..config import ConfigurationError, TelegramConfig, load_telegram_config
from ..logging_config import configure_logging, get_console_logger
from ..storage import resolve_db_path


def check_credentials_action(
    *,
    refresh_env: bool,
    generate_session: bool,
) -> int:
    """Validate environment configuration for Telegram access."""
    configure_logging("WARNING")
    console = get_console_logger()
    try:
        config = load_telegram_config(
            refresh_env=refresh_env,
            require_auth=not generate_session,
        )
    except ConfigurationError as err:
        console.error("Configuration error: %s", err)
        return 1

    db_env_raw = os.getenv("OSINTAGENCY_DB_PATH")
    db_override = db_env_raw if db_env_raw else None
    db_path = resolve_db_path(db_override)
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as err:
        console.error("Database path %s is not usable: %s", db_path, err)
        return 1

    if generate_session:
        session = _generate_session_string(config)
        if session is None:
            return 1
        console.info("Generated TELEGRAM_SESSION_STRING value:")
        console.info("%s", session)
        return 0

    console.info("Credential check succeeded.")
    console.info("Authentication mode: %s", config.auth_mode)
    console.info("Target channel id: %s", config.target_channel)
    if db_override:
        console.info("OSINTAGENCY_DB_PATH override: %s", db_path)
    else:
        console.info("Using default database path: %s", db_path)
    return 0


def _generate_session_string(config: TelegramConfig) -> str | None:
    """Interactively collect a Telethon session string."""
    console = get_console_logger()
    if config.session_string:
        console.warning(
            "Existing TELEGRAM_SESSION_STRING detected; generating a new one anyway.",
        )
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
    except ImportError:
        console.error(
            "Telethon must be installed to generate a session string.",
        )
        return None

    console.info(
        "Starting interactive Telethon login. You will be prompted for phone and login codes.",
    )
    try:
        with TelegramClient(StringSession(), config.api_id, config.api_hash) as client:
            client.start()
            return client.session.save()
    except Exception as err:  # noqa: BLE001 - surface all Telethon errors for debugging
        console.error("Failed to generate session string: %s", err)
        return None


__all__ = ["check_credentials_action"]
