"""Pytest configuration helpers."""

import os
import sys
from pathlib import Path

# Ensure the project root is importable so tests can resolve `osintagency`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Skip reading the repository `.env` file during test runs to keep fixtures isolated.
os.environ.setdefault("OSINTAGENCY_SKIP_DOTENV", "1")

# Import storage fixtures to make them available to all tests
pytest_plugins = ["tests.fixtures"]
