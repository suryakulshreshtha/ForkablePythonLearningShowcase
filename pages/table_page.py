"""
pages/table_page.py — Data Tables Page Object
===============================================
Demonstrates extracting and interacting with HTML tables.
Critical for data validation in enterprise applications.
"""

from playwright.sync_api import Page
from pages.base_page import BasePage


class TablePage(BasePage):
    """Handles HTML table extraction and sorting."""

    TABLE_1 = "#table1"
    TABLE_2 = "#table2"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/tables")
        return self

    def get_headers(self, table_id: str = "table1") -> list[str]:
        return self.page.locator(f"#{table_id} thead th").all_inner_texts()

    def get_row_count(self, table_id: str = "table1") -> int:
        return self.count_elements(f"#{table_id} tbody tr")

    def get_cell(self, table_id: str, row: int, col: int) -> str:
        """Get cell text by 0-based row and column index."""
        return self.page.locator(
            f"#{table_id} tbody tr:nth-child({row + 1}) td:nth-child({col + 1})"
        ).inner_text()

    def get_column_values(self, table_id: str, col_index: int) -> list[str]:
        """Extract all values from a specific column (0-based index)."""
        rows = self.page.locator(f"#{table_id} tbody tr")
        count = rows.count()
        return [
            rows.nth(i).locator("td").nth(col_index).inner_text()
            for i in range(count)
        ]

    def click_sort_header(self, column_name: str):
        """Click a column header to sort by it."""
        self.page.get_by_role("columnheader", name=column_name).click()
        return self

    def find_row_by_last_name(self, last_name: str) -> int:
        """Returns the 0-based row index of the first row matching the last name."""
        rows = self.page.locator(f"{self.TABLE_1} tbody tr")
        count = rows.count()
        for i in range(count):
            cell_text = rows.nth(i).locator("td").first.inner_text()
            if cell_text.strip() == last_name:
                return i
        return -1
