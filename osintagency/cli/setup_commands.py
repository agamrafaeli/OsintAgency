"""Setup command group for database and data initialization operations."""

from __future__ import annotations

import click

from .commands import cleanup_database as cleanup_database_module
from .decorators import osintagency_cli_command


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


__all__ = ["setup_group"]
