Actions Layer Notes
===================

- The CLI decorator `osintagency_cli_command` configures logging for Click entry points, but the action modules (`fetch_channel_action`, `check_credentials_action`) still call `configure_logging()` internally.
- Keeping the call inside each action ensures they behave correctly when invoked outside the CLI—such as tests, ad-hoc scripts, or other services—where the decorator is not present.
- If usage is ever restricted to CLI entry points only, reassess whether this guard remains necessary, but for now the redundancy is intentional.
