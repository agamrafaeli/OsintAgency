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
   pytest tests/test_fetch_channel.py -q
   ```
4. For verbose failure details during debugging, drop the `-q` flag and optionally add `-vv`.

## Managing the `tests/` Folder

- Keep all automated tests under `tests/` so they are collected automatically by `pytest`.
- Name new test files `test_<feature>.py` and group related helpers or fixtures in modules with descriptive names rather than step numbers.
- When adding fixtures or shared utilities, place them in `tests/conftest.py` (create it if needed) to keep them discoverable across all tests.
- Avoid committing cached bytecode (`__pycache__`); if it appears, remove it before committing.
- Store sample data or recorded responses under `tests/data/` (create the directory as needed) and document the data source inside that folder to keep provenance clear.

## Continuous Improvement

- When introducing a new feature or bug fix, add or update tests in the same commit so the change set documents its coverage.
- If the suite becomes slow, mark intentionally long-running tests with `@pytest.mark.slow` and add a `pytest.ini` marker definition so they can be isolated (`pytest -m "not slow"`).
- Capture regressions by converting manual debugging actions into repeatable tests whenever feasible.
