Centralized Logging Overview
============================

OSINT Agency agents rely on a shared logging helper in `osintagency/logging_config.py`.
The helper exposes two utilities:

* `configure_logging(level: str | int | None)` installs a single root configuration with
  stdout/stderr handlers. Call it once near process start (CLI entry points already do).
* `get_logger(name: str | None)` returns a standard module logger whose messages respect
  the configured log level.
* `get_console_logger()` returns a console logger for user-facing output. It always emits
  messages, ignoring the global level, while routing INFO and below to stdout and warnings
  or errors to stderr.

Implementation Guidelines
-------------------------

* Never call `print`; use the console logger for CLI output and the module logger for
  diagnostics.
* If code needs deterministic console output (e.g., JSON lines), emit it through the
  console logger to maintain capture compatibility in tests.
* Avoid reconfiguring handlers manually; extend `logging_config` if additional behaviour
  is required.
* Decorate Click entry points with `osintagency_cli_command(...)` to configure logging once per
  invocation and keep future validations centralized.
* When a command exposes a `--log-level` option, pass its parameter name via
  `log_level_param` so the decorator applies the desired verbosity before entering the action.
* Prefer `INFO` for standard operational logs that should appear during routine runs, `DEBUG`
  for verbose diagnostic traces during development, `WARNING` for recoverable issues, and
  `ERROR`/`CRITICAL` for failures that require operator attention. Default CLI behaviour
  keeps noise low by starting at `WARNING` unless callers request a lower level.
