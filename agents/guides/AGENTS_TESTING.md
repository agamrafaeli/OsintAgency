# Agent Testing Guide

This guide clarifies when to exercise the test suite and how to keep the shared `tests/` folder organized.

## When to Run the Suite

- Before committing or merging any change, run the full suite (`pytest`) from the project root.
- When developing a new capability, follow TDD: start with a failing test, make it pass, then rerun the full suite to confirm no regressions.
- After changing dependencies, environment variables, or external integrations (for example, channel credentials), rerun the suite to catch configuration drift.
- If you regenerate fixtures or stored data, run the suite to confirm the new assets are compatible.

## Running Tests Locally

1. Activate the project virtual environment and install dependencies with `pip install -r requirements.txt` if you have not already.
2. From the repository root, run the complete suite:
   ```bash
   pytest -q
   ```
3. To focus on a specific area while iterating, target an individual test module:
   ```bash
   pytest tests/cli/test_fetch_channel.py -q
   ```
4. For verbose failure details during debugging, drop the `-q` flag and optionally add `-vv`.

## Logging Expectations

- Use `get_console_logger()` in CLI-facing code so Click-based tests capture stdout JSON lines without parsing errors.
- When validating diagnostics, prefer `caplog` or `CliRunner` result logging over raw `print` calls to keep the central logger authoritative.
- Avoid calling `logging.basicConfig` inside tests; the shared configuration in `osintagency.logging_config` should stay in control unless a test explicitly resets handlers.

## Managing the `tests/` Folder

- Keep all automated tests under `tests/` so they are collected automatically by `pytest`.
- Organize tests into the following subdirectories:
  - `tests/unit/`: Isolated component tests (no external dependencies or complex interactions).
  - `tests/integration/`: Multi-component tests (e.g., involving storage, database, or multiple modules).
  - `tests/cli/`: Tests for CLI commands and interactions.
  - `tests/fixtures/`: Shared test utilities and fixtures.
- Name new test files `test_<feature>.py` and place them in the appropriate subdirectory.
- When adding fixtures or shared utilities, place them in `tests/conftest.py` or create dedicated fixture modules in `tests/fixtures/` (e.g., `tests/fixtures/fixtures.py`).
- Import fixture modules via `pytest_plugins` in `tests/conftest.py` to make them discoverable across all tests.
- Avoid committing cached bytecode (`__pycache__`); if it appears, remove it before committing.
- Store sample data or recorded responses under `tests/data/` (create the directory as needed) and document the data source inside that folder to keep provenance clear.

### Available Test Fixtures

The project provides reusable fixtures for database testing in `tests/fixtures/fixtures.py`:

- **`memory_db`**: Provides a temporary SQLite database file that is automatically cleaned up after each test. Use this for tests that need an isolated database.
- **`populated_db`**: Extends `memory_db` by pre-populating it with sample message data. Use this when tests need existing data without setup boilerplate.
- **`db_factory`**: Factory fixture for creating multiple isolated databases within a single test. Useful for testing multi-database scenarios.

### Storage Backend Testing

Storage integration tests in `tests/integration/test_storage.py` are parameterized to run against all storage backend implementations:

- Tests use the `storage_backend` fixture, which is parameterized with backend classes (currently `[PeeweeStorage]`).
- Tests are **backend-agnostic** and only interact through the `StorageBackend` interface.
- To add a new storage backend, implement the `StorageBackend` interface and add it to the fixture's `params` list.
- All backends must pass the same test suite, ensuring consistent behavior across implementations.
- Avoid backend-specific code in integration tests; if you need to test backend-specific features, create a separate test file.

## Continuous Improvement

- When introducing a new feature or bug fix, add or update tests in the same commit so the change set documents its coverage.
- If the suite becomes slow, mark intentionally long-running tests with `@pytest.mark.slow` and add a `pytest.ini` marker definition so they can be isolated (`pytest -m "not slow"`).
- Capture regressions by converting manual debugging actions into repeatable tests whenever feasible.
