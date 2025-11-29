"""Business action for listing suspect channels discovered from forward references."""

from __future__ import annotations

import json
import os

from ..logging_config import configure_logging, get_console_logger, get_logger
from ..storage import get_storage_backend

logger = get_logger(__name__)


def list_suspect_channels_action(
    *,
    db_path: str | os.PathLike[str] | None,
    log_level: str,
    output_format: str = "table",
    min_references: int = 1,
) -> int:
    """List channels discovered from forward references.

    Args:
        db_path: Path to the database file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        output_format: Output format ("table" or "json")
        min_references: Minimum number of references to include a channel

    Returns:
        Exit code (0 for success, 1 for error)
    """
    configure_logging(log_level)
    console = get_console_logger()

    try:
        # Fetch forwarded channels from storage
        backend = get_storage_backend(db_path=db_path)
        channels = backend.fetch_forwarded_channels()

        # Filter by minimum references
        if min_references > 1:
            channels = [
                channel for channel in channels
                if channel["reference_count"] >= min_references
            ]

        # Handle empty results
        if not channels:
            if output_format == "json":
                print(json.dumps([]))
            else:
                console.info("No suspect channels found.")
            return 0

        # Output results
        if output_format == "json":
            print(json.dumps(channels, indent=2))
        else:
            # Table format
            _print_table(channels)

        return 0

    except Exception:
        logger.exception("Failed to list suspect channels")
        console.error("Error: Failed to list suspect channels")
        return 1


def _print_table(channels: list[dict[str, object]]) -> None:
    """Print channels in table format."""
    # Header
    print(f"{'Channel ID':<20} {'References':<15}")
    print("-" * 35)

    # Rows
    for channel in channels:
        channel_id = str(channel["source_channel_id"])
        ref_count = str(channel["reference_count"])
        print(f"{channel_id:<20} {ref_count:<15}")


__all__ = ["list_suspect_channels_action"]
