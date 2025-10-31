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


def _normalize_args(argv: Sequence[str] | None) -> list[str]:
    if argv is None:
        return sys.argv[1:]
    return list(argv)


class OsintAgencyCLI:
    """Facade over individual CLI commands to enable reuse and testing."""

    def __init__(self, *, stdout=None, stderr=None) -> None:
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def fetch_channel(self, argv: Sequence[str] | None = None) -> int:
        """Persist deterministic messages or clean up the backing database."""
        args = _normalize_args(argv)
        try:
            return fetch_channel_command.main(
                args=args,
                prog_name="fetch_channel",
                standalone_mode=False,
                obj={"stdout": self._stdout, "stderr": self._stderr},
            )
        except click.ClickException as err:  # pragma: no cover - defensive
            err.show(file=self._stderr)
            return err.exit_code
        except SystemExit as err:  # pragma: no cover - defensive
            return err.code if isinstance(err.code, int) else 1

    def check_credentials(self, argv: Sequence[str] | None = None) -> int:
        """Validate environment configuration for Telegram access."""
        args = _normalize_args(argv)
        try:
            return check_credentials_command.main(
                args=args,
                prog_name="check_credentials",
                standalone_mode=False,
                obj={"stdout": self._stdout, "stderr": self._stderr},
            )
        except click.ClickException as err:  # pragma: no cover - defensive
            err.show(file=self._stderr)
            return err.exit_code
        except SystemExit as err:  # pragma: no cover - defensive
            return err.code if isinstance(err.code, int) else 1


@click.group()
def cli() -> None:
    """OSINT Agency command collection."""


cli.add_command(fetch_channel_command)
cli.add_command(check_credentials_command)


if __name__ == "__main__":  # pragma: no cover - module entry point
    cli()
