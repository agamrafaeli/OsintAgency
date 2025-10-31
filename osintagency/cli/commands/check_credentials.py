"""Command facade for validating Telegram credential configuration."""

from __future__ import annotations

from ...actions.check_credentials_action import check_credentials_action


def check_credentials_command(
    *,
    refresh_env: bool,
    generate_session: bool,
) -> int:
    """Invoke the check-credentials action with CLI-provided arguments."""
    return check_credentials_action(
        refresh_env=refresh_env,
        generate_session=generate_session,
    )


__all__ = ["check_credentials_command"]
