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

        # Initialize table with filtered data (Last 7d by default)
        verses_table = ui.table(
            columns=columns,
            rows=get_mock_verses(time_window="Last 7d"),
            row_key="sura"
        ).classes("w-full")

        # Event handlers that update the table with filtered mock data
        def on_time_window_change(e):
            """Handle time window selection changes."""
            new_time_window = e.value
            current_filter = text_filter.value or ""

            # Get filtered data
            filtered_verses = get_mock_verses(
                time_window=new_time_window,
                filter_text=current_filter
            )

            # Update table rows
            verses_table.rows = filtered_verses

            # Show notification
            ui.notify(f"Time window changed to: {new_time_window}")

        def on_filter_change(e):
            """Handle filter text input changes."""
            filter_text = e.value or ""
            current_time_window = time_window.value

            # Get filtered data
            filtered_verses = get_mock_verses(
                time_window=current_time_window,
                filter_text=filter_text
            )

            # Update table rows
            verses_table.rows = filtered_verses

            # Show notification with appropriate message
            if filter_text and len(filtered_verses) == 0:
                ui.notify("No verses match your filter", type="warning")
            elif filter_text:
                ui.notify(f"Filter updated: {filter_text} ({len(filtered_verses)} results)")
            else:
                ui.notify("Filter cleared")

        time_window.on("update:model-value", on_time_window_change)
        text_filter.on("update:model-value", on_filter_change)
