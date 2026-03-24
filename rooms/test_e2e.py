import pytest
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def django_server():
    """Start the Django development server for E2E testing"""
    subprocess.run(
        [sys.executable, "manage.py", "migrate"],
        check=True,
    )

    server_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "8000", "--noreload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    time.sleep(3)

    yield "http://localhost:8000"

    server_process.terminate()
    server_process.wait()


def test_room_list_page_loads_and_displays_heading(django_server):
    """E2E test: The room list page loads in a real browser and displays
    the 'Room List' heading"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(django_server)

        assert page.title() is not None

        heading = page.locator("h1")
        assert heading.is_visible()
        assert "Room List" in heading.text_content()

        browser.close()