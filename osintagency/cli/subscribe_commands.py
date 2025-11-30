"""Subscribe command group for managing channel subscriptions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import sys

import click

from ..actions.fetch_subscriptions_action import fetch_subscriptions_action
from ..clients import TelethonTelegramClient
from ..config import load_telegram_config
from ..subscription import (
    add_subscription,
    get_subscriptions,
    remove_subscription,
    update_subscription,
)
from .decorators import osintagency_cli_command


@click.group(name="subscribe")
def subscribe_group() -> None:
    """Manage channel subscriptions."""


@subscribe_group.command(name="add")
@click.option(
    "--channel-id",
    required=True,
    help="The Telegram channel identifier (e.g., @channel or numeric ID).",
)
@click.option(
    "--name",
    help="Human-readable channel name.",
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
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def add_command(
    ctx: click.Context,
    channel_id: str,
    name: str | None,
    db_path: str | None,
    log_level: str,
) -> None:
    """Add or update a channel subscription."""
    try:
        add_subscription(
            channel_id=channel_id,
            name=name,
            db_path=db_path,
        )
        print(f"Subscribed to {channel_id}")
    except Exception as e:
        print(f"Error subscribing to {channel_id}: {e}", file=sys.stderr)
        ctx.exit(1)


@subscribe_group.command(name="list")
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
    "--include-inactive",
    is_flag=True,
    help="Include inactive subscriptions in the output.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Output format.",
)
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def list_command(
    ctx: click.Context,
    db_path: str | None,
    log_level: str,
    include_inactive: bool,
    output_format: str,
) -> None:
    """List all channel subscriptions."""
    try:
        subscriptions = get_subscriptions(
            active_only=not include_inactive,
            db_path=db_path,
        )

        if not subscriptions:
            print("No subscriptions found.")
            return

        if output_format == "json":
            print(json.dumps(subscriptions, indent=2))
        else:
            # Table format
            print(f"{'Channel ID':<30} {'Name':<30} {'Active':<10} {'Added At':<25}")
            print("-" * 95)
            for sub in subscriptions:
                channel_id = str(sub["channel_id"])[:28]
                name = str(sub["name"] or "")[:28]
                active = "Yes" if sub["active"] else "No"
                added_at = str(sub["added_at"])[:23]
                print(f"{channel_id:<30} {name:<30} {active:<10} {added_at:<25}")
    except Exception as e:
        print(f"Error listing subscriptions: {e}", file=sys.stderr)
        ctx.exit(1)


@subscribe_group.command(name="update")
@click.option(
    "--channel-id",
    required=True,
    help="The Telegram channel identifier to update.",
)
@click.option(
    "--name",
    help="New human-readable channel name.",
)
@click.option(
    "--active/--inactive",
    default=None,
    help="Set subscription active status.",
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
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def update_command(
    ctx: click.Context,
    channel_id: str,
    name: str | None,
    active: bool | None,
    db_path: str | None,
    log_level: str,
) -> None:
    """Update an existing subscription."""
    try:
        # Check if at least one update parameter is provided
        if name is None and active is None:
            print("Error: At least one of --name or --active/--inactive must be provided.", file=sys.stderr)
            ctx.exit(1)

        success = update_subscription(
            channel_id=channel_id,
            name=name,
            active=active,
            db_path=db_path,
        )

        if success:
            print(f"Updated subscription for {channel_id}")
        else:
            print(f"Subscription not found for {channel_id}", file=sys.stderr)
            ctx.exit(1)
    except Exception as e:
        print(f"Error updating subscription for {channel_id}: {e}", file=sys.stderr)
        ctx.exit(1)


@subscribe_group.command(name="remove")
@click.option(
    "--channel-id",
    required=True,
    help="The Telegram channel identifier to remove.",
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
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def remove_command(
    ctx: click.Context,
    channel_id: str,
    db_path: str | None,
    log_level: str,
) -> None:
    """Remove a channel subscription."""
    try:
        success = remove_subscription(
            channel_id=channel_id,
            db_path=db_path,
        )

        if success:
            print(f"Removed subscription for {channel_id}")
        else:
            print(f"Subscription not found for {channel_id}", file=sys.stderr)
            ctx.exit(1)
    except Exception as e:
        print(f"Error removing subscription for {channel_id}: {e}", file=sys.stderr)
        ctx.exit(1)


@subscribe_group.command(name="fetch")
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
def fetch_command(
    ctx: click.Context,
    limit: int,
    db_path: str | None,
    log_level: str,
    days: int | None,
) -> None:
    """Fetch messages from all active subscribed channels."""
    telegram_client = None
    if ctx.obj:
        telegram_client = ctx.obj.get("telegram_client")

    if telegram_client is None:
        config = load_telegram_config(require_auth=True)
        telegram_client = TelethonTelegramClient(config)

    # Convert days to offset_date
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


__all__ = ["subscribe_group"]
