"""
Forwarded from & discovery panel for the dashboard.

This panel will display forwarded channels for discovery (currently placeholder).
"""
from nicegui import ui


def render_forwarded_panel():
    """Render the forwarded from & discovery panel."""
    with ui.card().classes("w-full"):
        ui.label("Forwarded from & discovery").classes("text-xl font-semibold mb-2")
        ui.label("(No data yet)").classes("text-gray-500")
