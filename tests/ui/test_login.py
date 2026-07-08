"""
tests/ui/test_login.py — Login Test Suite
==========================================
Demonstrates:
  - Positive and negative test cases
  - pytest.mark for categorisation
  - pytest.param for parametrized tests
  - Page Object injection via fixtures
  - Playwright assertions (expect)
"""

import re
import pytest
from pages.login_page import LoginPage
from pages.secure_page import SecurePage


# ─────────────────────────────────────────────────────────────────────────────
# Test Class — groups related tests, shares setup via class-level fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.login
class TestLogin:
    """
    Test suite for the Login functionality.
    Using a class lets pytest-html group these under one heading.
    """

    # ── Happy Path ────────────────────────────────────────────────────────────

    @pytest.mark.smoke
    def test_valid_login(self, page):
        """TC-001: Valid credentials should redirect to /secure."""
        login_page  = LoginPage(page).load()
        secure_page = SecurePage(page)

        login_page.login("tomsmith", "SuperSecretPassword!")
        secure_page.assert_on_secure_page()

    @pytest.mark.smoke
    def test_login_shows_success_flash(self, page):
        """TC-002: Successful login should display a success flash message."""
        login_page = LoginPage(page).load()
        login_page.login("tomsmith", "SuperSecretPassword!")

        assert "secure area" in login_page.get_flash_message().lower()

    # ── Negative Cases ────────────────────────────────────────────────────────

    @pytest.mark.regression
    def test_invalid_password(self, page):
        """TC-003: Wrong password should show an error, stay on login page."""
        login_page = LoginPage(page).load()
        login_page.login("tomsmith", "wrongpassword")

        login_page.assert_login_error("Your password is invalid!")

    @pytest.mark.regression
    def test_invalid_username(self, page):
        """TC-004: Wrong username should show an error."""
        login_page = LoginPage(page).load()
        login_page.login("nobody", "SuperSecretPassword!")

        login_page.assert_login_error("Your username is invalid!")

    @pytest.mark.regression
    def test_empty_credentials(self, page):
        """TC-005: Empty form submission should show validation error."""
        login_page = LoginPage(page).load()
        login_page.login("", "")

        assert login_page.is_error_shown(), "Error message not shown for empty credentials"

    # ── Parametrised Tests ────────────────────────────────────────────────────

    @pytest.mark.regression
    @pytest.mark.parametrize("username, password, expected_error", [
        ("",           "pass",   "Your username is invalid!"),
        ("tomsmith",   "",       "Your password is invalid!"),
        ("wronguser",  "wrongpw", "Your username is invalid!"),
        ("tomsmith",   "wrong",  "Your password is invalid!"),
    ], ids=["empty-user", "empty-pass", "bad-user", "bad-pass"])
    def test_invalid_login_combinations(self, page, username, password, expected_error):
        """TC-006: Parametrized — multiple invalid credential combinations."""
        login_page = LoginPage(page).load()
        login_page.login(username, password)
        login_page.assert_login_error(expected_error)

    # ── Logout Flow ───────────────────────────────────────────────────────────

    @pytest.mark.smoke
    @pytest.mark.e2e
    def test_login_and_logout(self, page):
        """TC-007: E2E flow — login → verify → logout → verify back on login."""
        login_page  = LoginPage(page).load()
        secure_page = SecurePage(page)

        # Login
        login_page.login("tomsmith", "SuperSecretPassword!")
        secure_page.assert_on_secure_page()

        # Logout
        secure_page.logout()

        # Verify back on login page
        from playwright.sync_api import expect
        expect(page).to_have_url(re.compile(r"/login$"))

    # ── Pre-authenticated Test ────────────────────────────────────────────────

    @pytest.mark.smoke
    def test_secure_area_with_auth_fixture(self, logged_in_page):
        """
        TC-008: Uses the session-scoped logged_in_page fixture.
        Login happens once; this test reuses the saved session.
        Significantly faster than logging in per test.
        """
        secure_page = SecurePage(logged_in_page)
        secure_page.load()
        secure_page.assert_on_secure_page()
