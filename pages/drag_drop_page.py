"""
pages/drag_drop_page.py — Drag and Drop Page Object
=====================================================
Demonstrates drag-and-drop interactions using Playwright's drag_to().
"""

from playwright.sync_api import Page
from pages.base_page import BasePage


class DragDropPage(BasePage):
    """Handles drag-and-drop between two columns."""

    COLUMN_A = "#column-a"
    COLUMN_B = "#column-b"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/drag_and_drop")
        return self

    def drag_a_to_b(self):
        """Drag column A onto column B."""
        self.drag_and_drop(self.COLUMN_A, self.COLUMN_B)
        return self

    def get_column_a_header(self) -> str:
        return self.get_text(f"{self.COLUMN_A} header")

    def get_column_b_header(self) -> str:
        return self.get_text(f"{self.COLUMN_B} header")
