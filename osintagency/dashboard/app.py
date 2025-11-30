"""
NiceGUI dashboard application for OSINT Agency.

This module provides a minimal NiceGUI web application with dashboard
route displaying analysis interface.
"""
from nicegui import ui
from .panels.verses_panel import render_verses_panel
from .panels.subscriptions_panel import render_subscriptions_panel
from .panels.forwarded_panel import render_forwarded_panel


@ui.page("/")
def index_page():
    """Root route - redirects to dashboard."""
    ui.navigate.to("/dashboard")


@ui.page("/dashboard")
def dashboard_page():
    """Dashboard route handler."""
    ui.label("Dashboard loaded").classes("text-2xl font-bold")

    # Panel 1: Top detected verses
    render_verses_panel()

    # Panel 2: Subscriptions & scraping
    render_subscriptions_panel()

    # Panel 3: Forwarded from & discovery
    render_forwarded_panel()


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
