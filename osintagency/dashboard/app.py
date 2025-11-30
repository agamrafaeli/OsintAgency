"""
NiceGUI dashboard application for OSINT Agency.

This module provides a minimal NiceGUI web application with a single
/dashboard route displaying a basic placeholder interface.
"""
from nicegui import ui


def create_dashboard_app():
    """
    Create and configure the NiceGUI dashboard application.

    Returns:
        The configured NiceGUI app instance.
    """

    @ui.page("/dashboard")
    def dashboard_page():
        """Dashboard route handler."""
        ui.page_title("Dashboard")

        with ui.column().classes("w-full p-4"):
            ui.label("Dashboard loaded").classes("text-2xl font-bold")

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
