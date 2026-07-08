"""
pages/dropdown_page.py — Dropdown Page Object
===============================================
Covers: select by value, by label, by index, verify selection.
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class DropdownPage(BasePage):
    """Demonstrates <select> dropdown interaction."""

    DROPDOWN = "#dropdown"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/dropdown")
        return self

    def select_by_value(self, value: str):
        self.select_option(self.DROPDOWN, value=value)
        return self

    def select_by_label(self, label: str):
        self.select_option(self.DROPDOWN, label=label)
        return self

    def select_by_index(self, index: int):
        self.select_option(self.DROPDOWN, index=index)
        return self

    def get_selected_value(self) -> str:
        return self.get_input_value(self.DROPDOWN)

    def get_selected_label(self) -> str:
        return self.page.locator(f"{self.DROPDOWN} option:checked").inner_text()

    def get_all_options(self) -> list[str]:
        """Returns text of all available dropdown options."""
        return self.page.locator(f"{self.DROPDOWN} option").all_inner_texts()

    def assert_selected(self, expected_value: str):
        expect(self.page.locator(self.DROPDOWN)).to_have_value(expected_value)
