"""
Subscriptions & scraping panel for the dashboard.

This panel manages channel subscriptions with action buttons and per-row controls.
"""
from nicegui import ui
from ..mock_data import get_mock_subscriptions


def render_subscriptions_panel():
    """Render the subscriptions & scraping panel."""
    with ui.card().classes("w-full"):
        ui.label("Subscriptions & scraping").classes("text-xl font-semibold mb-4")

        # Action buttons bar
        with ui.row().classes("gap-4 mb-4"):
            rescrape_all_btn = ui.button("Re-scrape all active channels").props("color=primary")
            full_reset_btn = ui.button("Full reset & re-scrape").props("color=warning")

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
            rows=get_mock_subscriptions(),
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
