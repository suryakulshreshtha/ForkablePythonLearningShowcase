"""
pages/checkbox_page.py — Checkboxes Page Object
=================================================
Covers: check, uncheck, verify state, toggle all.
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CheckboxPage(BasePage):
    """Demonstrates interaction with checkboxes."""

    CHECKBOXES = "input[type='checkbox']"
    CHECKBOX_1 = "input[type='checkbox']:nth-of-type(1)"
    CHECKBOX_2 = "input[type='checkbox']:nth-of-type(2)"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/checkboxes")
        return self

    def get_checkbox(self, index: int):
        """Get checkbox by 0-based index."""
        return self.page.locator(self.CHECKBOXES).nth(index)

    def check_all(self):
        """Ensure all checkboxes are checked."""
        count = self.count_elements(self.CHECKBOXES)
        for i in range(count):
            cb = self.page.locator(self.CHECKBOXES).nth(i)
            if not cb.is_checked():
                cb.check()
        return self

    def uncheck_all(self):
        """Ensure all checkboxes are unchecked."""
        count = self.count_elements(self.CHECKBOXES)
        for i in range(count):
            cb = self.page.locator(self.CHECKBOXES).nth(i)
            if cb.is_checked():
                cb.uncheck()
        return self

    def toggle_all(self):
        """Toggle the state of every checkbox."""
        count = self.count_elements(self.CHECKBOXES)
        for i in range(count):
            self.page.locator(self.CHECKBOXES).nth(i).click()
        return self

    def get_states(self) -> list[bool]:
        """Returns list of checked states for all checkboxes."""
        count = self.count_elements(self.CHECKBOXES)
        return [self.page.locator(self.CHECKBOXES).nth(i).is_checked() for i in range(count)]

    def assert_checkbox_count(self, expected: int):
        expect(self.page.locator(self.CHECKBOXES)).to_have_count(expected)
