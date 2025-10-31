from __future__ import annotations

import argparse

from osintagency.cli import create_fetch_channel_parser, parse_fetch_channel_args


def test_create_fetch_channel_parser_returns_argument_parser():
    parser = create_fetch_channel_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    args = parser.parse_args([])
    assert args.limit == 5
    assert args.channel is None
    assert args.db_path is None
    assert args.log_level == "WARNING"
    assert args.cleanup is False


def test_parse_fetch_channel_args_handles_overrides():
    args = parse_fetch_channel_args(
        [
            "--limit",
            "10",
            "--channel",
            "@other",
            "--db-path",
            "/tmp/messages.sqlite3",
            "--log-level",
            "info",
            "--cleanup",
        ]
    )

    assert args.limit == 10
    assert args.channel == "@other"
    assert args.db_path == "/tmp/messages.sqlite3"
    assert args.log_level == "info"
    assert args.cleanup is True
