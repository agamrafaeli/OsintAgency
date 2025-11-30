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
        ui.label("Top detected verses").classes("text-xl font-semibold mb-4")

        # Controls row: time window dropdown and text filter
        with ui.row().classes("gap-4 mb-4"):
            time_window = ui.select(
                options=["Last 24h", "Last 7d", "Last 30d", "All time"],
                value="Last 7d",
                label="Time window"
            ).classes("w-40")

            text_filter = ui.input(
                label="Filter verses",
                placeholder="Search sura, ayah..."
            ).classes("flex-grow")

        # Mock data for the verses table
        mock_verses = [
            {"sura": 1, "ayah": 1, "mentions": 42, "channels": 8, "first_seen": "2025-11-15", "last_seen": "2025-11-29"},
            {"sura": 2, "ayah": 255, "mentions": 38, "channels": 12, "first_seen": "2025-11-10", "last_seen": "2025-11-30"},
            {"sura": 3, "ayah": 185, "mentions": 25, "channels": 6, "first_seen": "2025-11-20", "last_seen": "2025-11-28"},
            {"sura": 18, "ayah": 10, "mentions": 19, "channels": 5, "first_seen": "2025-11-12", "last_seen": "2025-11-27"},
            {"sura": 36, "ayah": 82, "mentions": 15, "channels": 4, "first_seen": "2025-11-18", "last_seen": "2025-11-25"},
        ]

        # Verses table
        columns = [
            {"name": "sura", "label": "Sura", "field": "sura", "align": "left"},
            {"name": "ayah", "label": "Ayah", "field": "ayah", "align": "left"},
            {"name": "mentions", "label": "Total mentions", "field": "mentions", "align": "left"},
            {"name": "channels", "label": "Distinct channels", "field": "channels", "align": "left"},
            {"name": "first_seen", "label": "First seen", "field": "first_seen", "align": "left"},
            {"name": "last_seen", "label": "Last seen", "field": "last_seen", "align": "left"},
        ]

        verses_table = ui.table(
            columns=columns,
            rows=mock_verses,
            row_key="sura"
        ).classes("w-full")

        # Event handlers for mock interactions (log only, no real filtering)
        def on_time_window_change(e):
            ui.notify(f"Time window changed to: {e.value}")

        def on_filter_change(e):
            ui.notify(f"Filter updated: {e.value}")

        time_window.on("update:model-value", on_time_window_change)
        text_filter.on("update:model-value", on_filter_change)

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
