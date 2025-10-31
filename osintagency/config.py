"""Configuration helpers for Telegram access."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


class ConfigurationError(RuntimeError):
    """Raised when the environment is missing required configuration."""


@dataclass(frozen=True)
class TelegramConfig:
    """Normalized Telegram credential configuration."""

    api_id: int
    api_hash: str
    target_channel: str
    session_string: Optional[str]
    bot_token: Optional[str]

    @property
    def auth_mode(self) -> str:
        """Return which credential type is active."""
        return "session" if self.session_string else "bot"

    def require_session(self) -> None:
        """Ensure the configuration includes a user session string."""
        if not self.session_string:
            raise ConfigurationError(
                "TELEGRAM_SESSION_STRING is required for this operation."
            )


def load_telegram_config(
    refresh_env: bool = False, *, require_auth: bool = True
) -> TelegramConfig:
    """Load Telegram configuration from environment variables.

    Parameters
    ----------
    refresh_env:
        When True, reload values from the `.env` file even if already loaded.
    require_auth:
        When True (default) ensure either a session string or bot token is provided.
    """
    if refresh_env or not os.getenv("TELEGRAM_API_ID"):
        # Load .env only when first needed to avoid repeated disk work.
        load_dotenv()

    try:
        api_id_raw = _require("TELEGRAM_API_ID")
        api_id = int(api_id_raw)
    except ValueError as err:
        raise ConfigurationError("TELEGRAM_API_ID must be an integer.") from err

    api_hash = _require("TELEGRAM_API_HASH")
    target_channel = _require("TELEGRAM_TARGET_CHANNEL")

    session_string = os.getenv("TELEGRAM_SESSION_STRING")
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if require_auth and not session_string and not bot_token:
        raise ConfigurationError(
            "Provide either TELEGRAM_SESSION_STRING or TELEGRAM_BOT_TOKEN."
        )

    return TelegramConfig(
        api_id=api_id,
        api_hash=api_hash,
        target_channel=target_channel,
        session_string=session_string,
        bot_token=bot_token,
    )


def _require(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise ConfigurationError(f"Missing required environment variable: {key}")
    return value
