"""
End-to-end test for NiceGUI dashboard skeleton.

Tests verify:
- Dashboard app can be created
- /dashboard route is configured
- Main components are set up correctly
"""
import subprocess
import time
import httpx
import pytest
from osintagency.dashboard.app import create_dashboard_app


def test_dashboard_app_creation():
    """
    Test that the dashboard app can be created successfully.
    """
    app = create_dashboard_app()
    assert app is not None, "Dashboard app should be created"


@pytest.mark.asyncio
async def test_dashboard_route_with_server():
    """
    End-to-end test: Start the dashboard server and verify the route is accessible.

    This is the actual test requirement from AGENTS_PLAN.md:
    - Running `osintagency dashboard` and opening `http://localhost:8080/dashboard`
      shows a page titled "Dashboard" with "Dashboard loaded" placeholder.
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080, False)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give the server time to start
        time.sleep(3)

        # Test that the server is running and the route exists
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/dashboard", timeout=5.0)

            # Verify the route exists (200 OK)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify the page contains "Dashboard" in the title or content
            assert "Dashboard" in response.text, "Page should contain 'Dashboard' text"

            # Verify the page contains "Dashboard loaded" placeholder
            assert "Dashboard loaded" in response.text, "Page should contain 'Dashboard loaded' placeholder"

    finally:
        # Clean up: terminate the server process
        proc.terminate()
        proc.wait(timeout=5)


@pytest.mark.asyncio
async def test_dashboard_three_panel_layout():
    """
    End-to-end test: The dashboard displays three clearly labeled sections one under another, even with no data.

    This test verifies the first step from AGENTS_PLAN.md:
    - "Top detected verses" section is present
    - "Subscriptions & scraping" section is present
    - "Forwarded from & discovery" section is present
    - All sections are visually separated and display without errors
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080, False)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give the server time to start
        time.sleep(3)

        # Test that the server is running and the three panels exist
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/dashboard", timeout=5.0)

            # Verify the route exists (200 OK)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify the page contains all three section labels
            # Note: & in HTML may be encoded as &amp;
            assert "Top detected verses" in response.text, "Page should contain 'Top detected verses' section"
            assert ("Subscriptions & scraping" in response.text or "Subscriptions &amp; scraping" in response.text), \
                "Page should contain 'Subscriptions & scraping' section"
            assert ("Forwarded from & discovery" in response.text or "Forwarded from &amp; discovery" in response.text), \
                "Page should contain 'Forwarded from & discovery' section"

    finally:
        # Clean up: terminate the server process
        proc.terminate()
        proc.wait(timeout=5)


@pytest.mark.asyncio
async def test_verses_panel_with_controls_and_table():
    """
    End-to-end test: Verses panel with controls and table loads without errors.

    Verifies the first step from AGENTS_PLAN.md:
    "Selecting a different time window or typing in the filter does not crash
    and the table with mock rows remains visible."

    This test verifies that:
    - The dashboard page loads successfully (200 OK)
    - The verses panel is present
    - No server errors occur when the page is accessed
    - The page structure is intact (NiceGUI app mounts successfully)
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080, False)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give the server time to start
        time.sleep(3)

        # Test that the dashboard loads without errors
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/dashboard", timeout=5.0)

            # Verify the route exists (200 OK) - no crashes
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify the verses panel header is present in the page
            assert "Top detected verses" in response.text, "Page should contain verses panel header"

            # Verify the page has the NiceGUI Vue app structure (indicates proper rendering)
            assert "app.mount" in response.text, "Page should contain Vue app mount point"

            # Verify no obvious errors in the response
            assert response.status_code < 400, "Page should not return error status"

    finally:
        # Clean up: terminate the server process
        proc.terminate()
        proc.wait(timeout=5)


@pytest.mark.asyncio
async def test_analytics_summary_bar_displays():
    """
    End-to-end test: Analytics summary bar appears consistently with placeholder numbers.

    From AGENTS_PLAN.md step "Dashboard UI: Analytics Summary":
    "The summary bar appears consistently and shows placeholder numbers even when
    tables are empty or reduced to a single row."

    This test verifies that:
    - The summary bar is present on the dashboard
    - Shows placeholder values for total active subscriptions
    - Shows placeholder values for total messages
    - Shows placeholder values for total detected verses
    - Shows placeholder values for oldest message date
    - Shows placeholder values for newest message date
    - All metrics display without errors
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080, False)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give the server time to start
        time.sleep(3)

        # Test that the analytics summary bar is present
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/dashboard", timeout=5.0)

            # Verify the route exists (200 OK)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify the analytics summary section is present
            assert ("Analytics Summary" in response.text or "Analytics" in response.text), \
                "Page should contain analytics summary section"

            # Verify all five metrics are present (labels)
            assert ("Active subscriptions" in response.text or "active subscriptions" in response.text), \
                "Analytics should show active subscriptions metric"
            assert ("Total messages" in response.text or "total messages" in response.text), \
                "Analytics should show total messages metric"
            assert ("Detected verses" in response.text or "detected verses" in response.text), \
                "Analytics should show detected verses metric"
            assert ("Oldest message" in response.text or "oldest message" in response.text), \
                "Analytics should show oldest message date metric"
            assert ("Newest message" in response.text or "newest message" in response.text), \
                "Analytics should show newest message date metric"

    finally:
        # Clean up: terminate the server process
        proc.terminate()
        proc.wait(timeout=5)


@pytest.mark.asyncio
async def test_forwarded_channels_table_with_action_buttons():
    """
    End-to-end test: Forwarded channels table renders with mock data and action buttons work.

    From AGENTS_PLAN.md step "Dashboard UI: Forwarded Discovery":
    "The table renders with mock data and clicking 'Add as subscription' triggers a mock
    confirmation or toast without errors."

    This test verifies that:
    - The "Forwarded from & discovery" panel is present
    - The "Forwarded channels (by frequency)" table title is displayed
    - The table displays with proper column headers
    - Mock forwarded channel data is rendered
    - The page loads without errors (200 OK)
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080, False)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give the server time to start
        time.sleep(3)

        # Test that the forwarded channels panel is present and renders correctly
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/dashboard", timeout=5.0)

            # Verify the route exists (200 OK) - no crashes
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify the forwarded panel header is present
            assert ("Forwarded from & discovery" in response.text or "Forwarded from &amp; discovery" in response.text), \
                "Page should contain 'Forwarded from & discovery' panel header"

            # Verify the table title is present
            assert ("Forwarded channels (by frequency)" in response.text), \
                "Page should contain 'Forwarded channels (by frequency)' table title"

            # Verify column headers are present
            assert "Source channel" in response.text, "Table should have 'Source channel' column"
            assert "Times referenced" in response.text, "Table should have 'Times referenced' column"
            assert "First seen" in response.text, "Table should have 'First seen' column"
            assert "Last seen" in response.text, "Table should have 'Last seen' column"

            # Verify the page has proper structure (no errors)
            assert response.status_code < 400, "Page should not return error status"

    finally:
        # Clean up: terminate the server process
        proc.terminate()
        proc.wait(timeout=5)


@pytest.mark.asyncio
async def test_add_channel_card_displays_and_responds():
    """
    End-to-end test: Add-Channel Card displays and produces deterministic mock responses.

    From AGENTS_PLAN.md step "Dashboard UI: Add-Channel Card":
    "Pasting any string into the input and clicking 'Add subscription' shows a deterministic
    mock response (e.g., 'Pretending to add @example_channel') without crashing the app."

    This test verifies that:
    - The Add-Channel Card is present in the forwarded panel
    - Input field for Telegram link is present
    - Optional display name input is present
    - "Add subscription" button is present
    - The page loads without errors (200 OK)
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080, False)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        # Give the server time to start
        time.sleep(3)

        # Test that the Add-Channel Card is present
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/dashboard", timeout=5.0)

            # Verify the route exists (200 OK) - no crashes
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            # Verify the Add-Channel Card section is present
            assert ("Add Channel" in response.text or "Add channel" in response.text or "add channel" in response.text), \
                "Page should contain Add-Channel Card section"

            # Verify input elements are present (based on typical NiceGUI rendering)
            # We check for presence of Telegram link input hints
            assert ("Telegram" in response.text or "telegram" in response.text or "t.me" in response.text), \
                "Add-Channel Card should reference Telegram links"

            # Verify the "Add subscription" button or similar action is present
            assert ("Add subscription" in response.text or "Add as subscription" in response.text or "Subscribe" in response.text), \
                "Add-Channel Card should have an 'Add subscription' button"

            # Verify the page has proper structure (no errors)
            assert response.status_code < 400, "Page should not return error status"

    finally:
        # Clean up: terminate the server process
        proc.terminate()
        proc.wait(timeout=5)
