"""
NiceGUI dashboard application for OSINT Agency.

This module provides a minimal NiceGUI web application with dashboard
route displaying analysis interface.
"""
from nicegui import ui


@ui.page("/")
def index_page():
    """Root route - redirects to dashboard."""
    ui.navigate.to("/dashboard")


@ui.page("/dashboard")
def dashboard_page():
    """Dashboard route handler."""
    ui.label("Dashboard loaded").classes("text-2xl font-bold")

    # Panel 1: Top detected verses
    with ui.card().classes("w-full"):
        ui.label("Top detected verses").classes("text-xl font-semibold mb-2")
        ui.label("(No data yet)").classes("text-gray-500")

    # Panel 2: Subscriptions & scraping
    with ui.card().classes("w-full"):
        ui.label("Subscriptions & scraping").classes("text-xl font-semibold mb-2")
        ui.label("(No data yet)").classes("text-gray-500")

    # Panel 3: Forwarded from & discovery
    with ui.card().classes("w-full"):
        ui.label("Forwarded from & discovery").classes("text-xl font-semibold mb-2")
        ui.label("(No data yet)").classes("text-gray-500")


def create_dashboard_app():
    """
    Create and configure the NiceGUI dashboard application.

    Returns:
        The configured NiceGUI app instance.
    """
    # Page routes are registered at module level via @ui.page decorator
    return ui


def run_dashboard(host: str = "127.0.0.1", port: int = 8080):
    """
    Run the dashboard server.

    Args:
        host: Host address to bind to (default: 127.0.0.1)
        port: Port to listen on (default: 8080)
    """
    create_dashboard_app()
    ui.run(
        host=host,
        port=port,
        title="OSINT Agency Dashboard",
        show=True,
        reload=False,
    )
