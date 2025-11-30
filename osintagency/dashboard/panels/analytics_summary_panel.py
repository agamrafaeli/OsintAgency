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

    def on_metric_click(metric_name: str):
        """
        Handle metric card clicks.

        Logs the action and shows a notification for future filtering functionality.
        TODO: Implement actual filtering/navigation logic when backend supports it.
        """
        ui.notify(f"Future feature: Filter by {metric_name}", type="info")

    with ui.card().classes("w-full mb-6"):
        ui.label("Analytics Summary").classes("text-xl font-semibold mb-4")

        # Summary metrics displayed in a grid layout
        with ui.grid(columns=5).classes("gap-4 w-full"):
            # Metric 1: Active subscriptions
            with ui.card().classes("p-4 cursor-pointer") as card1:
                card1.on("click", lambda: on_metric_click("active subscriptions"))
                ui.label("Active subscriptions").classes("text-sm text-gray-600").tooltip(
                    "Number of Telegram channels currently being monitored for new messages"
                )
                ui.label(str(analytics["active_subscriptions"])).classes(
                    "text-2xl font-bold"
                )

            # Metric 2: Total messages
            with ui.card().classes("p-4 cursor-pointer") as card2:
                card2.on("click", lambda: on_metric_click("total messages"))
                ui.label("Total messages").classes("text-sm text-gray-600").tooltip(
                    "Total count of messages collected across all subscribed channels"
                )
                ui.label(str(analytics["total_messages"])).classes(
                    "text-2xl font-bold"
                )

            # Metric 3: Detected verses
            with ui.card().classes("p-4 cursor-pointer") as card3:
                card3.on("click", lambda: on_metric_click("detected verses"))
                ui.label("Detected verses").classes("text-sm text-gray-600").tooltip(
                    "Number of unique Quranic verses identified in collected messages"
                )
                ui.label(str(analytics["detected_verses"])).classes(
                    "text-2xl font-bold"
                )

            # Metric 4: Oldest message date
            with ui.card().classes("p-4 cursor-pointer") as card4:
                card4.on("click", lambda: on_metric_click("oldest message date"))
                ui.label("Oldest message").classes("text-sm text-gray-600").tooltip(
                    "Date of the earliest message in the database"
                )
                ui.label(analytics["oldest_message_date"]).classes(
                    "text-lg font-semibold"
                )

            # Metric 5: Newest message date
            with ui.card().classes("p-4 cursor-pointer") as card5:
                card5.on("click", lambda: on_metric_click("newest message date"))
                ui.label("Newest message").classes("text-sm text-gray-600").tooltip(
                    "Date of the most recent message in the database"
                )
                ui.label(analytics["newest_message_date"]).classes(
                    "text-lg font-semibold"
                )
