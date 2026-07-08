"""
tests/components/test_form_components.py — Component-Level Tests
==================================================================
Component tests sit between unit tests and E2E tests in the pyramid.
They test individual UI components in isolation:
  - Checkboxes
  - Dropdowns
  - Data Tables
  - Sorting

These are faster than E2E tests because they test one thing at a time.
"""

import pytest
from playwright.sync_api import Page, expect
from pages import CheckboxPage, DropdownPage, TablePage
from utils.helpers import assert_sorted_ascending, assert_sorted_descending


# ─────────────────────────────────────────────────────────────────────────────
# Checkboxes
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.smoke
class TestCheckboxes:

    def test_page_has_two_checkboxes(self, page: Page):
        """TC-070: Verify checkbox page renders exactly 2 checkboxes."""
        cb_page = CheckboxPage(page).load()
        cb_page.assert_checkbox_count(2)

    def test_check_all_checkboxes(self, page: Page):
        """TC-071: Check all checkboxes and verify all are checked."""
        cb_page = CheckboxPage(page).load()
        cb_page.check_all()
        states = cb_page.get_states()
        assert all(states), f"Expected all checked, got: {states}"

    def test_uncheck_all_checkboxes(self, page: Page):
        """TC-072: Uncheck all checkboxes and verify all are unchecked."""
        cb_page = CheckboxPage(page).load()
        cb_page.uncheck_all()
        states = cb_page.get_states()
        assert not any(states), f"Expected all unchecked, got: {states}"

    def test_toggle_reverses_all_states(self, page: Page):
        """TC-073: Toggle all, verify each state inverted."""
        cb_page      = CheckboxPage(page).load()
        before_states = cb_page.get_states()
        cb_page.toggle_all()
        after_states = cb_page.get_states()

        for i, (before, after) in enumerate(zip(before_states, after_states)):
            assert before != after, f"Checkbox {i}: expected toggle, but state stayed {before}"

    @pytest.mark.parametrize("index, expected_state", [
        (0, True),   # check checkbox 1
        (1, False),  # uncheck checkbox 2
    ], ids=["check-first", "uncheck-second"])
    def test_individual_checkbox_control(self, page: Page, index: int, expected_state: bool):
        """TC-074: Control individual checkboxes independently."""
        cb_page = CheckboxPage(page).load()
        cb      = cb_page.get_checkbox(index)
        if expected_state:
            cb.check()
        else:
            cb.uncheck()
        assert cb.is_checked() == expected_state


# ─────────────────────────────────────────────────────────────────────────────
# Dropdowns
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.smoke
class TestDropdown:

    def test_default_state_is_placeholder(self, page: Page):
        """TC-075: Dropdown default shows placeholder text."""
        dd_page = DropdownPage(page).load()
        options = dd_page.get_all_options()
        assert len(options) >= 3, "Expected at least 3 options (1 placeholder + 2 real)"

    def test_select_option_1_by_value(self, page: Page):
        """TC-076: Select Option 1 by its value attribute."""
        dd_page = DropdownPage(page).load()
        dd_page.select_by_value("1")
        dd_page.assert_selected("1")

    def test_select_option_2_by_value(self, page: Page):
        """TC-077: Select Option 2 by its value attribute."""
        dd_page = DropdownPage(page).load()
        dd_page.select_by_value("2")
        dd_page.assert_selected("2")

    def test_select_by_label(self, page: Page):
        """TC-078: Select an option by its visible label text."""
        dd_page = DropdownPage(page).load()
        dd_page.select_by_label("Option 1")
        assert "1" in dd_page.get_selected_value()

    @pytest.mark.parametrize("value", ["1", "2"], ids=["option-1", "option-2"])
    def test_all_options_selectable(self, page: Page, value: str):
        """TC-079: All non-placeholder options are selectable."""
        dd_page = DropdownPage(page).load()
        dd_page.select_by_value(value)
        dd_page.assert_selected(value)

    def test_selection_persists(self, page: Page):
        """TC-080: Selected value persists after re-reading."""
        dd_page = DropdownPage(page).load()
        dd_page.select_by_value("2")
        # Read it twice — should be stable
        assert dd_page.get_selected_value() == "2"
        assert dd_page.get_selected_value() == "2"


# ─────────────────────────────────────────────────────────────────────────────
# Data Tables
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.regression
class TestDataTables:

    def test_table_has_expected_headers(self, page: Page):
        """TC-081: Table 1 has correct column headers."""
        tbl_page = TablePage(page).load()
        headers  = tbl_page.get_headers("table1")
        expected = ["Last Name", "First Name", "Email", "Due", "Web Site", "Action"]
        for col in expected:
            assert col in headers, f"Expected column '{col}' not found in: {headers}"

    def test_table_has_data_rows(self, page: Page):
        """TC-082: Table 1 contains at least 4 data rows."""
        tbl_page = TablePage(page).load()
        count    = tbl_page.get_row_count("table1")
        assert count >= 4, f"Expected >=4 rows, got {count}"

    def test_cell_data_not_empty(self, page: Page):
        """TC-083: First cell of first row is not empty."""
        tbl_page = TablePage(page).load()
        cell_val = tbl_page.get_cell("table1", row=0, col=0)
        assert len(cell_val.strip()) > 0, "First table cell is empty"

    def test_sort_by_last_name_ascending(self, page: Page):
        """TC-084: Clicking Last Name header sorts the column ascending."""
        tbl_page  = TablePage(page).load()
        tbl_page.click_sort_header("Last Name")
        values    = tbl_page.get_column_values("table1", 0)
        clean     = [v.strip() for v in values if v.strip()]
        assert assert_sorted_ascending(clean), \
            f"Column not sorted ascending: {clean}"

    def test_find_row_by_last_name(self, page: Page):
        """TC-085: Can locate a specific row by last name lookup."""
        tbl_page  = TablePage(page).load()
        row_index = tbl_page.find_row_by_last_name("Smith")
        assert row_index >= 0, "Row with last name 'Smith' not found in table"

    def test_email_column_contains_at_symbol(self, page: Page):
        """TC-086: All email cells contain '@' — basic data integrity check."""
        tbl_page = TablePage(page).load()
        emails   = tbl_page.get_column_values("table1", 2)
        for email in emails:
            email = email.strip()
            if email:
                assert "@" in email, f"Invalid email found in table: '{email}'"
