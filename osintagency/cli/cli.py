"""Executable entry points for OSINT Agency CLI commands."""

from __future__ import annotations

import click

from .commands import check_credentials as check_credentials_module
from .commands import fetch_channel as fetch_channel_module
from .decorators import osintagency_cli_command
from .setup_commands import setup_group
from .subscribe_commands import subscribe_group


@click.command(name="fetch-channel")
@click.option(
    "--limit",
    type=int,
    default=5,
    show_default=True,
    help="Number of recent posts to retrieve.",
)
@click.option(
    "--channel-id",
    help="Override the target channel id or username defined in the environment.",
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
    help="Fetch only messages from the last N days.",
)
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def fetch_channel_command(
    ctx: click.Context,
    limit: int,
    channel_id: str | None,
    db_path: str | None,
    log_level: str,
    use_stub: bool,
    days: int | None,
) -> None:
    """Persist Telegram messages into the configured store."""
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


@click.command(name="check-credentials")
@click.option(
    "--refresh-env",
    is_flag=True,
    help="Reload values from the .env file instead of using cached values.",
)
@click.option(
    "--generate-session",
    is_flag=True,
    help=(
        "Interactively generate a TELEGRAM_SESSION_STRING using the App API. "
        "Requires TELEGRAM_API_ID and TELEGRAM_API_HASH to be configured."
    ),
)
@click.pass_context
@osintagency_cli_command()
def check_credentials_command(
    ctx: click.Context,
    refresh_env: bool,
    generate_session: bool,
) -> None:
    """Validate environment configuration for Telegram access."""
    exit_code = check_credentials_module.check_credentials_command(
        refresh_env=refresh_env,
        generate_session=generate_session,
    )
    ctx.exit(exit_code)


@click.group()
def cli() -> None:
    """OSINT Agency command collection."""


cli.add_command(fetch_channel_command)
cli.add_command(check_credentials_command)
cli.add_command(setup_group)
cli.add_command(subscribe_group)


if __name__ == "__main__":  # pragma: no cover - module entry point
    cli()
