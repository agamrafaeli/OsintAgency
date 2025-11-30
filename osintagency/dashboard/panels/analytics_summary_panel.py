"""
Analytics summary panel for the dashboard.

This panel displays aggregated analytics with placeholder values for total
active subscriptions, messages, detected verses, and date ranges.
"""
from nicegui import ui
from ..mock_data import get_mock_analytics_summary


def render_analytics_summary_panel():
    """Render the analytics summary bar with key metrics."""
    analytics = get_mock_analytics_summary()

    with ui.card().classes("w-full mb-6"):
        ui.label("Analytics Summary").classes("text-xl font-semibold mb-4")

        # Summary metrics displayed in a grid layout
        with ui.grid(columns=5).classes("gap-4 w-full"):
            # Metric 1: Active subscriptions
            with ui.card().classes("p-4"):
                ui.label("Active subscriptions").classes("text-sm text-gray-600")
                ui.label(str(analytics["active_subscriptions"])).classes(
                    "text-2xl font-bold"
                )

            # Metric 2: Total messages
            with ui.card().classes("p-4"):
                ui.label("Total messages").classes("text-sm text-gray-600")
                ui.label(str(analytics["total_messages"])).classes(
                    "text-2xl font-bold"
                )

            # Metric 3: Detected verses
            with ui.card().classes("p-4"):
                ui.label("Detected verses").classes("text-sm text-gray-600")
                ui.label(str(analytics["detected_verses"])).classes(
                    "text-2xl font-bold"
                )

            # Metric 4: Oldest message date
            with ui.card().classes("p-4"):
                ui.label("Oldest message").classes("text-sm text-gray-600")
                ui.label(analytics["oldest_message_date"]).classes(
                    "text-lg font-semibold"
                )

            # Metric 5: Newest message date
            with ui.card().classes("p-4"):
                ui.label("Newest message").classes("text-sm text-gray-600")
                ui.label(analytics["newest_message_date"]).classes(
                    "text-lg font-semibold"
                )
