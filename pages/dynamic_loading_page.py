"""
pages/dynamic_loading_page.py — Dynamic Content / AJAX Page Object
===================================================================
Demonstrates waiting for dynamically loaded elements — one of the
most critical patterns in real-world automation.
"""

from playwright.sync_api import Page
from pages.base_page import BasePage


class DynamicLoadingPage(BasePage):
    """Handles dynamically loaded (AJAX) elements."""

    START_BUTTON    = "#start button"
    LOADING_SPINNER = "#loading"
    FINISH_TEXT     = "#finish h4"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self, example_number: int = 1):
        """Load example 1 (hidden element) or example 2 (element rendered after)."""
        self.navigate(f"/dynamic_loading/{example_number}")
        return self

    def click_start(self):
        self.click(self.START_BUTTON)
        return self

    def wait_for_finish(self) -> str:
        """
        Wait for the loading spinner to disappear, then return the finish text.
        This is the canonical pattern for AJAX waits in Playwright.
        """
        self.page.locator(self.LOADING_SPINNER).wait_for(state="hidden", timeout=15_000)
        self.page.locator(self.FINISH_TEXT).wait_for(state="visible", timeout=10_000)
        return self.get_text(self.FINISH_TEXT)

    def assert_hello_world(self):
        finish = self.wait_for_finish()
        assert "Hello World!" in finish, f"Expected 'Hello World!' but got: {finish}"
