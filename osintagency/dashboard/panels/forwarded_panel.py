"""
Forwarded from & discovery panel for the dashboard.

This panel displays forwarded channels for discovery with action buttons.
"""
from nicegui import ui
from ..mock_data import get_mock_forwarded_channels


def render_forwarded_panel():
    """Render the forwarded from & discovery panel."""
    with ui.card().classes("w-full"):
        ui.label("Forwarded from & discovery").classes("text-xl font-semibold mb-4")
        ui.label("Forwarded channels (by frequency)").classes("text-lg font-medium mb-2")

        # Forwarded channels table columns
        forwarded_columns = [
            {"name": "source_channel", "label": "Source channel", "field": "source_channel", "align": "left"},
            {"name": "times_referenced", "label": "Times referenced", "field": "times_referenced", "align": "right"},
            {"name": "first_seen", "label": "First seen", "field": "first_seen", "align": "left"},
            {"name": "last_seen", "label": "Last seen", "field": "last_seen", "align": "left"},
            {"name": "actions", "label": "Actions", "field": "actions", "align": "center"},
        ]

        forwarded_table = ui.table(
            columns=forwarded_columns,
            rows=get_mock_forwarded_channels(),
            row_key="source_channel"
        ).classes("w-full")

        # Add per-row action buttons using table slots
        # Show "Add as subscription" button for channels not subscribed, otherwise show "Subscribed" label
        forwarded_table.add_slot('body-cell-actions', r'''
            <q-td :props="props">
                <q-btn v-if="!props.row.already_subscribed"
                       size="sm" color="primary" flat dense label="Add as subscription"
                       @click="$parent.$emit('add-subscription', props.row)" />
                <span v-else class="text-gray-500">Subscribed</span>
            </q-td>
        ''')

        # Mock event handler for adding subscription
        def on_add_subscription(e):
            source_channel = e.args.get('source_channel', 'unknown')
            ui.notify(f"Mock: Adding {source_channel} as subscription...", type="positive")

        # Wire up event handler
        forwarded_table.on('add-subscription', on_add_subscription)
