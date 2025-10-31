#!/usr/bin/env python3
"""Fetch recent posts from a Telegram channel using a deterministic stub."""

from __future__ import annotations

import json
import logging

from osintagency.cli import parse_fetch_channel_args
from osintagency.collector import collect_with_stub, purge_database_file
from osintagency.storage import resolve_db_path


logger = logging.getLogger(__name__)


def main() -> int:
    args = parse_fetch_channel_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.WARNING))

    if args.cleanup:
        target = resolve_db_path(args.db_path)
        removed = purge_database_file(db_path=target)
        if removed:
            logger.info("Removed database at %s", target)
        else:
            logger.info("No database found at %s", target)
        return 0

    try:
        outcome = collect_with_stub(
            limit=args.limit, channel_override=args.channel, db_path=args.db_path
        )
    except Exception:  # noqa: BLE001 - bubbled to the console and exit code
        logger.exception("Deterministic collection failed.")
        return 1

    logger.info(
        "Persisted %d message(s) for %s at %s",
        outcome.stored_messages,
        outcome.channel_id,
        outcome.db_path,
    )

    for message in outcome.messages:
        print(json.dumps(message, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
