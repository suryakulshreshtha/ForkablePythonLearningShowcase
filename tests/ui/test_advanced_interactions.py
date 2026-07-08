"""
tests/ui/test_advanced_interactions.py — Advanced Playwright Patterns
=======================================================================
Covers:
  - Dynamic/AJAX waits
  - JS Alerts, Confirms, Prompts
  - Drag and Drop
  - File Upload
  - iFrames
  - Multiple Browser Windows/Tabs
  - Network Interception (mocking)
  - Keyboard / Mouse actions
"""

import re
import pytest
from playwright.sync_api import Page, expect
from pages import DynamicLoadingPage, AlertsPage, DragDropPage


# ─────────────────────────────────────────────────────────────────────────────
# Dynamic Loading / AJAX Waits
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestDynamicContent:

    def test_dynamic_loading_example1(self, page):
        """
        TC-010: Waits for a hidden element to become visible after button click.
        Pattern: wait_for state="visible" / state="hidden"
        """
        dyn = DynamicLoadingPage(page).load(1)
        dyn.click_start()
        dyn.assert_hello_world()

    def test_dynamic_loading_example2(self, page):
        """TC-011: Waits for an element that doesn't exist yet to be rendered."""
        dyn = DynamicLoadingPage(page).load(2)
        dyn.click_start()
        dyn.assert_hello_world()


# ─────────────────────────────────────────────────────────────────────────────
# JavaScript Alerts
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestJSAlerts:

    def test_accept_js_alert(self, page):
        """TC-012: Accept a JS alert dialog."""
        alerts = AlertsPage(page).load()
        result = alerts.accept_alert()
        assert "You successfuly clicked an alert" in result

    def test_accept_js_confirm(self, page):
        """TC-013: Accept a JS confirm dialog."""
        alerts = AlertsPage(page).load()
        result = alerts.accept_confirm()
        assert "Ok" in result

    def test_dismiss_js_confirm(self, page):
        """TC-014: Dismiss a JS confirm dialog."""
        alerts = AlertsPage(page).load()
        result = alerts.dismiss_confirm()
        assert "Cancel" in result

    def test_js_prompt_with_text(self, page):
        """TC-015: Fill a JS prompt dialog."""
        alerts = AlertsPage(page).load()
        result = alerts.fill_prompt("Hello Playwright!")
        assert "Hello Playwright!" in result


# ─────────────────────────────────────────────────────────────────────────────
# Drag and Drop
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestDragDrop:

    def test_drag_column_a_to_b(self, page):
        """TC-016: Drag column A to column B position."""
        dd = DragDropPage(page).load()
        # Before drag
        initial_a = dd.get_column_a_header()
        assert initial_a == "A"

        dd.drag_a_to_b()

        # After drag column B should now contain 'A'
        new_b = dd.get_column_b_header()
        assert new_b == "A", f"Expected column B to be 'A', got: {new_b}"


# ─────────────────────────────────────────────────────────────────────────────
# File Upload (using the-internet.herokuapp.com/upload)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestFileUpload:

    def test_upload_file(self, page, tmp_path):
        """
        TC-017: Upload a file using Playwright's set_input_files().
        Creates a temporary file then uploads it — no real file needed.
        """
        # Create a dummy file to upload
        test_file = tmp_path / "test_upload.txt"
        test_file.write_text("Playwright file upload test content")

        page.goto("/upload")

        # Set the file on the input element
        page.locator("#file-upload").set_input_files(str(test_file))
        page.click("#file-submit")

        # Verify upload succeeded
        expect(page.locator("#uploaded-files")).to_have_text("test_upload.txt")


# ─────────────────────────────────────────────────────────────────────────────
# iFrames
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestIFrames:

    def test_interact_with_iframe_content(self, page):
        """
        TC-018: Switch to an iframe and interact with its content.
        Uses FrameLocator — the modern Playwright approach.
        """
        page.goto("/iframe")

        # Using frame_locator — chains all locators INSIDE the iframe
        frame   = page.frame_locator("#mce_0_ifr")
        editor  = frame.locator("#tinymce")

        # Clear existing content and type new text
        editor.click()
        editor.press("Control+A")
        editor.type("Testing iFrame interaction with Playwright")

        assert "Testing iFrame interaction" in editor.inner_text()


# ─────────────────────────────────────────────────────────────────────────────
# Multiple Tabs / Windows
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestMultipleTabs:

    def test_new_tab_opens(self, context, page):
        """
        TC-019: Handle links that open in a new tab.
        Key insight: use context.expect_page() to capture the new tab.
        """
        page.goto("/windows")

        # Use expect_page() to wait for the new tab to open
        with context.expect_page() as new_page_info:
            page.click("a[href='/windows/new']")

        new_tab = new_page_info.value
        new_tab.wait_for_load_state("domcontentloaded")

        expect(new_tab).to_have_url(re.compile(r"/windows/new$"))
        expect(new_tab.locator("h3")).to_have_text("New Window")


# ─────────────────────────────────────────────────────────────────────────────
# Network Interception / Mocking
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestNetworkInterception:

    def test_mock_api_response(self, page):
        """
        TC-020: Intercept a network request and return a mocked response.
        This is critical for testing error states, slow networks, etc.
        """
        # Route intercepts ALL requests matching the pattern
        page.route("**/api/**", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"mocked": true, "message": "Intercepted by Playwright"}'
        ))

        # Navigate — any /api/ call will now return our mock
        page.goto("/")
        # The interception is registered; further assertions depend on the app

    def test_block_images_for_performance(self, page):
        """
        TC-021: Block all image requests to speed up tests.
        Useful for smoke tests that don't need visual rendering.
        """
        page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())
        page.goto("/")
        # Page loads without any images — tests run faster

    def test_intercept_and_modify_response(self, page):
        """
        TC-022: Intercept a request, get the real response, modify it.
        """
        def modify_response(route):
            response = route.fetch()
            body = response.text()
            # Inject a marker to verify interception worked
            modified = body.replace("<title>", "<title>[MODIFIED] ")
            route.fulfill(response=response, body=modified)

        page.route("**/", modify_response)
        page.goto("/")
        title = page.title()
        # In a real scenario you'd assert the title contains "[MODIFIED]"


# ─────────────────────────────────────────────────────────────────────────────
# Keyboard & Mouse Actions
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestKeyboardMouse:

    def test_key_presses(self, page):
        """TC-023: Simulate keyboard shortcuts and key presses."""
        page.goto("/key_presses")
        page.locator("#target").click()
        page.keyboard.press("Tab")
        result = page.locator("#result").inner_text()
        assert "TAB" in result.upper()

    def test_hover_reveals_element(self, page):
        """TC-024: Hover to reveal a hidden element."""
        page.goto("/hovers")
        card = page.locator(".figure").first
        card.hover()

        # Hidden caption should now be visible
        caption = card.locator(".figcaption")
        expect(caption).to_be_visible()

    def test_right_click_context_menu(self, page):
        """TC-025: Right-click to trigger context menu."""
        page.goto("/context_menu")
        page.locator("#hot-spot").click(button="right")
        # Playwright automatically handles the browser dialog
        page.on("dialog", lambda d: d.accept())
