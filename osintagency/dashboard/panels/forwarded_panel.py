"""
Forwarded from & discovery panel for the dashboard.

This panel displays forwarded channels for discovery with action buttons.
"""
import re
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

        # Add-Channel Card - below the forwarded channels table
        ui.label("Add channel").classes("text-lg font-medium mt-6 mb-2")

        with ui.card().classes("w-full p-4"):
            ui.label("Add a new Telegram channel subscription").classes("text-sm text-gray-600 mb-4")

            # Telegram link input
            telegram_link_input = ui.input(
                label="Telegram link (e.g., https://t.me/channel_name)",
                placeholder="https://t.me/example_channel"
            ).classes("w-full mb-2")

            # Parsed channel display (reactive)
            parsed_channel_label = ui.label("").classes("text-sm text-gray-500 mb-2")

            # Optional display name input
            display_name_input = ui.input(
                label="Display name (optional)",
                placeholder="e.g., Example Channel"
            ).classes("w-full mb-4")

            # Helper function to parse Telegram link
            def parse_telegram_link(link: str) -> str:
                """
                Parse a Telegram link to extract the channel identifier.
                This is a mock implementation with deterministic behavior.

                Args:
                    link: The Telegram link string

                Returns:
                    The parsed channel identifier (e.g., @channel_name)
                """
                if not link:
                    return ""

                # Simple regex to extract channel name from various Telegram link formats
                # Supports: https://t.me/channel, t.me/channel, @channel, or plain channel
                patterns = [
                    r't\.me/([a-zA-Z0-9_]+)',  # t.me/channel
                    r'@([a-zA-Z0-9_]+)',        # @channel
                    r'^([a-zA-Z0-9_]+)$'        # plain channel name
                ]

                for pattern in patterns:
                    match = re.search(pattern, link)
                    if match:
                        channel_name = match.group(1)
                        return f"@{channel_name}"

                # If no pattern matches, use the input as-is with @ prefix
                return f"@{link.strip()}"

            # Update parsed channel when link changes
            def on_link_change():
                parsed = parse_telegram_link(telegram_link_input.value or "")
                if parsed:
                    parsed_channel_label.text = f"Channel: {parsed}"
                else:
                    parsed_channel_label.text = ""

            telegram_link_input.on('input', lambda: on_link_change())

            # Check if channel already exists (mock deterministic logic)
            def is_channel_already_subscribed(channel: str) -> bool:
                """
                Mock function to check if channel is already subscribed.
                Uses deterministic logic for testing.

                Args:
                    channel: The channel identifier

                Returns:
                    True if already subscribed (deterministically)
                """
                # Deterministic mock: channels containing "test" or "existing" are already subscribed
                existing_keywords = ["test", "existing", "subscribed"]
                channel_lower = channel.lower()
                return any(keyword in channel_lower for keyword in existing_keywords)

            # Add subscription button handler
            def on_add_subscription_click():
                link = telegram_link_input.value or ""
                parsed_channel = parse_telegram_link(link)
                display_name = display_name_input.value or ""

                if not parsed_channel or parsed_channel == "@":
                    ui.notify("Please enter a valid Telegram link", type="warning")
                    return

                # Mock deterministic response
                if is_channel_already_subscribed(parsed_channel):
                    ui.notify(
                        f"Channel {parsed_channel} already exists in subscriptions",
                        type="info"
                    )
                else:
                    display_text = display_name if display_name else parsed_channel
                    ui.notify(
                        f"Pretending to add {parsed_channel} ('{display_text}') as subscription",
                        type="positive"
                    )

                # Clear inputs after action
                telegram_link_input.value = ""
                display_name_input.value = ""
                parsed_channel_label.text = ""

            # Add subscription button
            ui.button("Add subscription", on_click=on_add_subscription_click).classes("bg-blue-500 text-white")
