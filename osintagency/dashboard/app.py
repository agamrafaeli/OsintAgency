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
        ui.label("Subscriptions & scraping").classes("text-xl font-semibold mb-4")

        # Action buttons bar
        with ui.row().classes("gap-4 mb-4"):
            rescrape_all_btn = ui.button("Re-scrape all active channels").props("color=primary")
            full_reset_btn = ui.button("Full reset & re-scrape").props("color=warning")

        # Mock data for subscriptions table
        mock_subscriptions = [
            {
                "channel_id": "@example_channel_1",
                "name": "Tech News Daily",
                "active": True,
                "messages_stored": 1523,
                "verses_detected": 42,
                "first_message_date": "2025-10-15",
                "last_message_date": "2025-11-30",
                "last_scrape_at": "2025-11-30 14:35:22"
            },
            {
                "channel_id": "@example_channel_2",
                "name": "Islamic Studies",
                "active": True,
                "messages_stored": 3847,
                "verses_detected": 215,
                "first_message_date": "2025-09-01",
                "last_message_date": "2025-11-29",
                "last_scrape_at": "2025-11-29 22:10:15"
            },
            {
                "channel_id": "@example_channel_3",
                "name": "Community Chat",
                "active": False,
                "messages_stored": 892,
                "verses_detected": 8,
                "first_message_date": "2025-11-10",
                "last_message_date": "2025-11-20",
                "last_scrape_at": "2025-11-20 09:45:00"
            },
            {
                "channel_id": "@example_channel_4",
                "name": "Quran Reflections",
                "active": True,
                "messages_stored": 2156,
                "verses_detected": 387,
                "first_message_date": "2025-08-20",
                "last_message_date": "2025-11-30",
                "last_scrape_at": "2025-11-30 16:20:44"
            },
        ]

        # Subscriptions table columns
        sub_columns = [
            {"name": "channel_id", "label": "Channel ID", "field": "channel_id", "align": "left"},
            {"name": "name", "label": "Name", "field": "name", "align": "left"},
            {"name": "active", "label": "Active", "field": "active", "align": "center"},
            {"name": "messages_stored", "label": "Messages stored", "field": "messages_stored", "align": "right"},
            {"name": "verses_detected", "label": "Verses detected", "field": "verses_detected", "align": "right"},
            {"name": "first_message_date", "label": "First message date", "field": "first_message_date", "align": "left"},
            {"name": "last_message_date", "label": "Last message date", "field": "last_message_date", "align": "left"},
            {"name": "last_scrape_at", "label": "Last scrape at", "field": "last_scrape_at", "align": "left"},
            {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
        ]

        subscriptions_table = ui.table(
            columns=sub_columns,
            rows=mock_subscriptions,
            row_key="channel_id"
        ).classes("w-full")

        # Add per-row action buttons using table slots
        subscriptions_table.add_slot('body-cell-actions', r'''
            <q-td :props="props">
                <q-btn size="sm" color="primary" flat dense label="Re-scrape"
                       @click="$parent.$emit('rescrape', props.row)" class="q-mr-xs" />
                <q-btn size="sm" color="secondary" flat dense label="Edit"
                       @click="$parent.$emit('edit', props.row)" class="q-mr-xs" />
                <q-btn size="sm" :color="props.row.active ? 'negative' : 'positive'"
                       flat dense :label="props.row.active ? 'Deactivate' : 'Activate'"
                       @click="$parent.$emit('toggle-active', props.row)" />
            </q-td>
        ''')

        # Mock event handlers for global buttons
        def on_rescrape_all_click():
            ui.notify("Mock: Re-scraping all active channels...", type="info")

        def on_full_reset_click():
            ui.notify("Mock: Full reset & re-scrape initiated...", type="warning")

        # Mock event handlers for per-row actions
        def on_row_rescrape(e):
            channel_id = e.args.get('channel_id', 'unknown')
            ui.notify(f"Mock: Re-scraping channel {channel_id}...", type="info")

        def on_row_edit(e):
            channel_id = e.args.get('channel_id', 'unknown')
            ui.notify(f"Mock: Editing channel {channel_id}...", type="info")

        def on_row_toggle_active(e):
            channel_id = e.args.get('channel_id', 'unknown')
            is_active = e.args.get('active', False)
            action = "Deactivating" if is_active else "Activating"
            ui.notify(f"Mock: {action} channel {channel_id}...", type="info")

        # Wire up event handlers
        rescrape_all_btn.on_click(on_rescrape_all_click)
        full_reset_btn.on_click(on_full_reset_click)
        subscriptions_table.on('rescrape', on_row_rescrape)
        subscriptions_table.on('edit', on_row_edit)
        subscriptions_table.on('toggle-active', on_row_toggle_active)

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
