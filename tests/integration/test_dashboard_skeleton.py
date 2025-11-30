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
    - Running `python main.py` and opening `http://localhost:8080/dashboard`
      shows a page titled "Dashboard" with "Dashboard loaded" placeholder.
    """
    # Start the dashboard server in a subprocess
    proc = subprocess.Popen(
        ["python", "-c", "from osintagency.dashboard.app import run_dashboard; run_dashboard('127.0.0.1', 8080)"],
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
