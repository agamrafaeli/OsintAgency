"""CLI command to run the NiceGUI dashboard."""
import click
from osintagency.dashboard.app import run_dashboard


@click.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="Host address to bind to",
    show_default=True,
)
@click.option(
    "--port",
    default=8080,
    type=int,
    help="Port to listen on",
    show_default=True,
)
def dashboard(host: str, port: int):
    """Run the OSINT Agency web dashboard."""
    click.echo(f"Starting dashboard at http://{host}:{port}")
    run_dashboard(host=host, port=port)
