"""Executable entry points for OSINT Agency CLI commands."""

from __future__ import annotations

import click

from .commands import check_credentials as check_credentials_module
from .commands import fetch_channel as fetch_channel_module
from .decorators import osintagency_cli_command


@click.command(name="fetch-channel")
@click.option(
    "--limit",
    type=int,
    default=5,
    show_default=True,
    help="Number of recent posts to retrieve.",
)
@click.option(
    "--channel",
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
    "--cleanup",
    is_flag=True,
    help="Delete the configured message store instead of collecting messages.",
)
@click.pass_context
@osintagency_cli_command(log_level_param="log_level")
def fetch_channel_command(
    ctx: click.Context,
    limit: int,
    channel: str | None,
    db_path: str | None,
    log_level: str,
    cleanup: bool,
) -> None:
    """Persist deterministic messages or clean up the backing database."""
    telegram_client = None
    if ctx.obj:
        telegram_client = ctx.obj.get("telegram_client")
    exit_code = fetch_channel_module.fetch_channel_command(
        limit=limit,
        channel=channel,
        db_path=db_path,
        log_level=log_level,
        cleanup=cleanup,
        telegram_client=telegram_client,
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


if __name__ == "__main__":  # pragma: no cover - module entry point
    cli()
