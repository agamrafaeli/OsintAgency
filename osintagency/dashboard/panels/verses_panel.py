"""
Top detected verses panel for the dashboard.

This panel displays the most frequently mentioned Quran verses with filtering options.
"""
from nicegui import ui
from ..mock_data import get_mock_verses


def render_verses_panel():
    """Render the top detected verses panel."""
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

        # Verses table columns
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
            rows=get_mock_verses(),
            row_key="sura"
        ).classes("w-full")

        # Event handlers for mock interactions (log only, no real filtering)
        def on_time_window_change(e):
            ui.notify(f"Time window changed to: {e.value}")

        def on_filter_change(e):
            ui.notify(f"Filter updated: {e.value}")

        time_window.on("update:model-value", on_time_window_change)
        text_filter.on("update:model-value", on_filter_change)
