"""Command-line parser helpers for project scripts."""

from __future__ import annotations

import argparse
from typing import Iterable, Sequence


def create_fetch_channel_parser() -> argparse.ArgumentParser:
    """Build the ArgumentParser for the fetch_channel CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Persist deterministic Telegram channel messages without hitting the network."
        )
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of recent posts to retrieve (default: 5).",
    )
    parser.add_argument(
        "--channel",
        help="Override the target channel id or username defined in the environment.",
    )
    parser.add_argument(
        "--db-path",
        help="Explicit database path override. Falls back to OSINTAGENCY_DB_PATH when omitted.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        help="Python logging level (default: WARNING).",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete the configured message store instead of collecting messages.",
    )
    return parser


def parse_fetch_channel_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:
    """Parse CLI arguments for the fetch_channel script."""
    parser = create_fetch_channel_parser()
    return parser.parse_args(argv)

