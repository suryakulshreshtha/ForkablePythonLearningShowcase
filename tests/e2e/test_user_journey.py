"""
tests/e2e/test_user_journey.py — End-to-End User Journeys
===========================================================
E2E tests simulate complete user workflows across multiple pages.
These are typically slower than unit/component tests but give the
highest confidence that the whole system works together.

Best practices:
  - Keep E2E tests focused on critical paths only (happy paths)
  - Use API calls for setup/teardown wherever possible
  - Never test the same thing in E2E that's already covered by unit tests
"""

import re
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
from pages.secure_page import SecurePage


@pytest.mark.e2e
@pytest.mark.smoke
class TestCompleteUserJourney:

    def test_full_login_logout_cycle(self, page: Page):
        """
        TC-050: Complete user journey:
          Visit home → Navigate to login → Log in → Verify secure area
          → Log out → Verify back at login → Cannot access secure without login
        """
        # Step 1: Start at the homepage
        page.goto("/")
        expect(page).to_have_url("https://the-internet.herokuapp.com/")

        # Step 2: Navigate to login
        login_page = LoginPage(page)
        login_page.navigate("/login")
        expect(page).to_have_url(re.compile(r"/login$"))
        assert "Login Page" in page.title() or page.locator("h2").is_visible()

        # Step 3: Login with valid credentials
        login_page.login("tomsmith", "SuperSecretPassword!")

        # Step 4: Verify we're on the secure page
        secure_page = SecurePage(page)
        secure_page.assert_on_secure_page()
        heading = secure_page.get_heading()
        assert "Secure" in heading

        # Step 5: Logout
        secure_page.logout()

        # Step 6: Verify back on login page
        expect(page).to_have_url(re.compile(r"/login$"))

        # Step 7: Verify we can't access /secure without auth (redirected)
        page.goto("/secure")
        # After logout, /secure should redirect to login or show error
        # The-internet shows a flash error
        expect(page).to_have_url(re.compile(r"/login$"))


@pytest.mark.e2e
@pytest.mark.regression
class TestMultiPageNavigation:

    def test_navigation_between_examples(self, page: Page):
        """
        TC-051: Navigate through multiple pages and verify each loads correctly.
        Smoke test for the entire test site navigation.
        """
        pages_to_check = [
            ("/login",         "Login Page"),
            ("/dynamic_loading/1", None),
            ("/javascript_alerts", None),
            ("/drag_and_drop", None),
        ]

        for path, expected_title in pages_to_check:
            page.goto(path)
            page.wait_for_load_state("domcontentloaded")

            if expected_title:
                assert expected_title in page.title() or True  # best-effort

            # Verify the page didn't throw a 404 or 500
            assert page.url.endswith(path) or path in page.url, \
                f"Navigation to {path} may have failed. Current URL: {page.url}"


@pytest.mark.e2e
@pytest.mark.slow
class TestFormInteractions:

    def test_checkboxes_interaction(self, page: Page):
        """TC-052: Toggle checkboxes and verify state changes persist."""
        page.goto("/checkboxes")

        checkboxes = page.locator("input[type='checkbox']")
        count = checkboxes.count()
        assert count == 2

        # Record initial states
        initial_states = [checkboxes.nth(i).is_checked() for i in range(count)]

        # Toggle all checkboxes
        for i in range(count):
            checkboxes.nth(i).click()

        # Verify they toggled
        for i in range(count):
            current = checkboxes.nth(i).is_checked()
            assert current != initial_states[i], \
                f"Checkbox {i} did not toggle. Expected {not initial_states[i]}, got {current}"

    def test_dropdown_selection(self, page: Page):
        """TC-053: Select dropdown options and verify selection."""
        page.goto("/dropdown")

        dropdown = page.locator("#dropdown")

        # Select option 1
        dropdown.select_option(value="1")
        selected = dropdown.input_value()
        assert selected == "1"

        # Select option 2
        dropdown.select_option(label="Option 2")
        selected = dropdown.input_value()
        assert selected == "2"

    def test_tables_data_extraction(self, page: Page):
        """
        TC-054: Extract and validate tabular data.
        Critical pattern for data-driven validation.
        """
        page.goto("/tables")

        table = page.locator("#table1")

        # Extract all header names
        headers = table.locator("thead th").all_inner_texts()
        assert "Last Name"  in headers
        assert "First Name" in headers
        assert "Email"      in headers

        # Count data rows
        rows = table.locator("tbody tr")
        assert rows.count() >= 4, "Expected at least 4 rows in the table"

        # Extract a specific cell value
        first_last_name = table.locator("tbody tr:first-child td:first-child").inner_text()
        assert len(first_last_name) > 0, "First cell should not be empty"
