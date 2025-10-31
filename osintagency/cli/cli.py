"""Executable entry points for OSINT Agency CLI commands."""

from __future__ import annotations

import sys
from contextlib import redirect_stderr, redirect_stdout
from typing import Sequence

import click

from .commands import check_credentials as check_credentials_module
from .commands import fetch_channel as fetch_channel_module


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
def fetch_channel_command(
    ctx: click.Context,
    limit: int,
    channel: str | None,
    db_path: str | None,
    log_level: str,
    cleanup: bool,
) -> int:
    """Persist deterministic messages or clean up the backing database."""
    io_context = ctx.ensure_object(dict)
    stdout = io_context.get("stdout", sys.stdout)
    stderr = io_context.get("stderr", sys.stderr)
    with redirect_stdout(stdout), redirect_stderr(stderr):
        return fetch_channel_module.fetch_channel_command(
            limit=limit,
            channel=channel,
            db_path=db_path,
            log_level=log_level,
            cleanup=cleanup,
        )


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
def check_credentials_command(
    ctx: click.Context,
    refresh_env: bool,
    generate_session: bool,
) -> int:
    """Validate environment configuration for Telegram access."""
    io_context = ctx.ensure_object(dict)
    stdout = io_context.get("stdout", sys.stdout)
    stderr = io_context.get("stderr", sys.stderr)
    with redirect_stdout(stdout), redirect_stderr(stderr):
        return check_credentials_module.check_credentials_command(
            refresh_env=refresh_env,
            generate_session=generate_session,
        )


@click.group()
def cli() -> None:
    """OSINT Agency command collection."""


cli.add_command(fetch_channel_command)
cli.add_command(check_credentials_command)


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout=None,
    stderr=None,
    prog_name: str = "osintagency",
) -> int:
    """Invoke the OSINT Agency CLI with optional stream overrides."""
    args = list(argv) if argv is not None else None
    io_context = {
        "stdout": stdout or sys.stdout,
        "stderr": stderr or sys.stderr,
    }
    try:
        return cli.main(
            args=args,
            prog_name=prog_name,
            standalone_mode=False,
            obj=io_context,
        )
    except click.ClickException as err:  # pragma: no cover - defensive
        err.show(file=io_context["stderr"])
        return err.exit_code
    except SystemExit as err:  # pragma: no cover - defensive
        return err.code if isinstance(err.code, int) else 1


if __name__ == "__main__":  # pragma: no cover - module entry point
    cli()
