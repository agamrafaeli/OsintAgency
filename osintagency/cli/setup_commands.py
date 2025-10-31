"""Setup command group for database and data initialization operations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import click

from .commands import cleanup_database as cleanup_database_module
from .commands import fetch_channel as fetch_channel_module
from .decorators import osintagency_cli_command
from ..actions.fetch_subscriptions_action import fetch_subscriptions_action
from ..collector import TelethonTelegramClient
from ..config import load_telegram_config


@click.group(name="setup")
def setup_group() -> None:
    """Setup and data initialization commands."""


@setup_group.command(name="cleanup")
@click.option(
    "--db-path",
    help="Explicit database path override. Falls back to OSINTAGENCY_DB_PATH when omitted.",
)
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    help="Python logging level.",
)
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def cleanup_command(
    ctx: click.Context,
    db_path: str | None,
    log_level: str,
) -> None:
    """Delete the configured message store."""
    exit_code = cleanup_database_module.cleanup_database_command(
        db_path=db_path,
        log_level=log_level,
    )
    ctx.exit(exit_code)


@setup_group.command(name="fetch-channel")
@click.argument("channel_id")
@click.option(
    "--limit",
    type=int,
    default=5,
    show_default=True,
    help="Number of recent posts to retrieve.",
)
@click.option(
    "--db-path",
    help="Explicit database path override. Falls back to OSINTAGENCY_DB_PATH when omitted.",
)
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    help="Python logging level.",
)
@click.option(
    "--use-stub",
    is_flag=True,
    help="Use the deterministic stub collector instead of live Telegram data.",
)
@click.option(
    "--days",
    type=int,
    default=30,
    show_default=True,
    help="Fetch only messages from the last N days.",
)
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def fetch_channel_command(
    ctx: click.Context,
    channel_id: str,
    limit: int,
    db_path: str | None,
    log_level: str,
    use_stub: bool,
    days: int,
) -> None:
    """Fetch Telegram messages for a specified channel."""
    telegram_client = None
    if ctx.obj:
        telegram_client = ctx.obj.get("telegram_client")
    exit_code = fetch_channel_module.fetch_channel_command(
        limit=limit,
        channel_id=channel_id,
        db_path=db_path,
        log_level=log_level,
        use_stub=use_stub,
        telegram_client=telegram_client,
        days=days,
    )
    ctx.exit(exit_code)


@setup_group.command(name="fetch-all")
@click.option(
    "--limit",
    type=int,
    default=5,
    show_default=True,
    help="Number of recent posts to retrieve from each channel.",
)
@click.option(
    "--db-path",
    help="Explicit database path override. Falls back to OSINTAGENCY_DB_PATH when omitted.",
)
@click.option(
    "--log-level",
    default="WARNING",
    show_default=True,
    help="Python logging level.",
)
@click.option(
    "--days",
    type=int,
    help="Fetch only messages from the last N days.",
)
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def fetch_all_command(
    ctx: click.Context,
    limit: int,
    db_path: str | None,
    log_level: str,
    days: int | None,
) -> None:
    """Fetch Telegram messages for all active subscriptions."""
    telegram_client = None
    if ctx.obj:
        telegram_client = ctx.obj.get("telegram_client")

    if telegram_client is None:
        config = load_telegram_config(require_auth=True)
        telegram_client = TelethonTelegramClient(config)

    offset_date = None
    if days is not None:
        offset_date = datetime.now(timezone.utc) - timedelta(days=days)

    exit_code = fetch_subscriptions_action(
        limit=limit,
        db_path=db_path,
        log_level=log_level,
        telegram_client=telegram_client,
        offset_date=offset_date,
    )
    ctx.exit(exit_code)


__all__ = ["setup_group"]
