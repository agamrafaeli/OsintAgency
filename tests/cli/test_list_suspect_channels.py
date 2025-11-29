"""Tests for the list-suspect-channels CLI command."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
import pytest

from osintagency.cli import cli


@pytest.fixture(autouse=True)
def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configure test environment variables."""
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")


def test_list_suspect_channels_table_format(tmp_path, monkeypatch):
    """Test that list-suspect-channels displays channels in table format."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Mock the storage backend to return sample data
    mock_data = [
        {"source_channel_id": 1005381772, "reference_count": 3},
        {"source_channel_id": 1234567890, "reference_count": 2},
        {"source_channel_id": 9876543210, "reference_count": 1},
    ]

    with patch("osintagency.actions.list_suspect_channels_action.get_storage_backend") as mock_backend:
        mock_instance = MagicMock()
        mock_instance.fetch_forwarded_channels.return_value = mock_data
        mock_backend.return_value = mock_instance

        result = runner.invoke(cli, ["list-suspect-channels"])

    assert result.exit_code == 0
    assert "Channel ID" in result.output
    assert "References" in result.output
    assert "1005381772" in result.output
    assert "3" in result.output
    assert "1234567890" in result.output
    assert "2" in result.output
    assert "9876543210" in result.output
    assert "1" in result.output


def test_list_suspect_channels_json_format(tmp_path, monkeypatch):
    """Test that list-suspect-channels supports JSON output format."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Mock the storage backend to return sample data
    mock_data = [
        {"source_channel_id": 1005381772, "reference_count": 3},
        {"source_channel_id": 1234567890, "reference_count": 2},
    ]

    with patch("osintagency.actions.list_suspect_channels_action.get_storage_backend") as mock_backend:
        mock_instance = MagicMock()
        mock_instance.fetch_forwarded_channels.return_value = mock_data
        mock_backend.return_value = mock_instance

        result = runner.invoke(cli, ["list-suspect-channels", "--format", "json"])

    assert result.exit_code == 0
    # Verify it's valid JSON
    output_data = json.loads(result.output)
    assert len(output_data) == 2
    assert output_data[0]["source_channel_id"] == 1005381772
    assert output_data[0]["reference_count"] == 3
    assert output_data[1]["source_channel_id"] == 1234567890
    assert output_data[1]["reference_count"] == 2


def test_list_suspect_channels_empty_results(tmp_path, monkeypatch):
    """Test that list-suspect-channels handles empty results gracefully."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Mock the storage backend to return empty data
    with patch("osintagency.actions.list_suspect_channels_action.get_storage_backend") as mock_backend:
        mock_instance = MagicMock()
        mock_instance.fetch_forwarded_channels.return_value = []
        mock_backend.return_value = mock_instance

        result = runner.invoke(cli, ["list-suspect-channels"])

    assert result.exit_code == 0
    assert "No suspect channels found" in result.output or "0" in result.output


def test_list_suspect_channels_min_references_filter(tmp_path, monkeypatch):
    """Test that list-suspect-channels filters by minimum references."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Mock the storage backend to return sample data
    mock_data = [
        {"source_channel_id": 1005381772, "reference_count": 3},
        {"source_channel_id": 1234567890, "reference_count": 2},
        {"source_channel_id": 9876543210, "reference_count": 1},
    ]

    with patch("osintagency.actions.list_suspect_channels_action.get_storage_backend") as mock_backend:
        mock_instance = MagicMock()
        mock_instance.fetch_forwarded_channels.return_value = mock_data
        mock_backend.return_value = mock_instance

        result = runner.invoke(cli, ["list-suspect-channels", "--min-references", "2"])

    assert result.exit_code == 0
    # Should only show channels with 2+ references
    assert "1005381772" in result.output
    assert "1234567890" in result.output
    assert "9876543210" not in result.output


def test_list_suspect_channels_custom_db_path(tmp_path, monkeypatch):
    """Test that list-suspect-channels respects custom db-path parameter."""
    monkeypatch.setenv("OSINTAGENCY_SKIP_DOTENV", "1")
    custom_db_path = tmp_path / "custom" / "database.sqlite3"
    runner = CliRunner()

    mock_data = [
        {"source_channel_id": 1111111111, "reference_count": 5},
    ]

    with patch("osintagency.actions.list_suspect_channels_action.get_storage_backend") as mock_backend:
        mock_instance = MagicMock()
        mock_instance.fetch_forwarded_channels.return_value = mock_data
        mock_backend.return_value = mock_instance

        result = runner.invoke(
            cli,
            ["list-suspect-channels", "--db-path", str(custom_db_path)],
        )

        # Verify the backend was called with the custom path
        mock_backend.assert_called_with(db_path=str(custom_db_path))

    assert result.exit_code == 0
    assert "1111111111" in result.output


def test_list_suspect_channels_storage_error(tmp_path, monkeypatch):
    """Test that list-suspect-channels handles storage errors gracefully."""
    db_path = tmp_path / "test.sqlite3"
    monkeypatch.setenv("OSINTAGENCY_DB_PATH", str(db_path))
    runner = CliRunner()

    # Mock the storage backend to raise an error
    with patch("osintagency.actions.list_suspect_channels_action.get_storage_backend") as mock_backend:
        mock_instance = MagicMock()
        mock_instance.fetch_forwarded_channels.side_effect = Exception("Database error")
        mock_backend.return_value = mock_instance

        result = runner.invoke(cli, ["list-suspect-channels"])

    assert result.exit_code != 0
