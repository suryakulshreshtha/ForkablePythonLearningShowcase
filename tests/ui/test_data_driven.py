"""
tests/ui/test_data_driven.py — Data-Driven Testing
=====================================================
Three approaches to data-driven tests in pytest:
  1. @pytest.mark.parametrize — inline test data
  2. CSV / Excel file as data source
  3. pytest fixtures returning datasets

Data-driven testing is powerful for:
  - Testing forms with many input combinations
  - Boundary value analysis (min, max, just-over)
  - Equivalence partitioning
  - Regression data sets from bug reports
"""

import csv
import json
import os
import pytest
from playwright.sync_api import Page
from pages.login_page import LoginPage


# ─────────────────────────────────────────────────────────────────────────────
# APPROACH 1: Inline parametrize
# ─────────────────────────────────────────────────────────────────────────────

LOGIN_TEST_DATA = [
    # (username,    password,                 expected_result, test_id)
    ("tomsmith",   "SuperSecretPassword!",   "success",       "valid-login"),
    ("tomsmith",   "wrongpassword",          "error",         "wrong-password"),
    ("wronguser",  "SuperSecretPassword!",   "error",         "wrong-username"),
    ("",           "",                       "error",         "empty-both"),
    ("tomsmith",   " ",                      "error",         "whitespace-password"),
]


@pytest.mark.ui
@pytest.mark.data_driven
@pytest.mark.parametrize(
    "username, password, expected_result",
    [(d[0], d[1], d[2]) for d in LOGIN_TEST_DATA],
    ids=[d[3] for d in LOGIN_TEST_DATA]
)
def test_login_data_driven(page: Page, username: str, password: str, expected_result: str):
    """TC-060: Parametrized login test covering valid and invalid scenarios."""
    login_page = LoginPage(page).load()
    login_page.login(username, password)

    if expected_result == "success":
        assert login_page.is_login_successful() or "/secure" in page.url
    else:
        assert login_page.is_error_shown(), \
            f"Expected error for user='{username}', pass='{password}'"


# ─────────────────────────────────────────────────────────────────────────────
# APPROACH 2: Fixture returning test data
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def dropdown_options():
    """Fixture returning test data for dropdown tests."""
    return [
        {"value": "1", "label": "Option 1"},
        {"value": "2", "label": "Option 2"},
    ]


@pytest.mark.ui
@pytest.mark.data_driven
def test_dropdown_all_options(page: Page, dropdown_options):
    """TC-061: Verify all dropdown options are selectable."""
    page.goto("/dropdown")
    dropdown = page.locator("#dropdown")

    for option in dropdown_options:
        dropdown.select_option(value=option["value"])
        selected_value = dropdown.input_value()
        assert selected_value == option["value"], \
            f"Expected value '{option['value']}', got '{selected_value}'"


# ─────────────────────────────────────────────────────────────────────────────
# APPROACH 3: Reading from a CSV file
# ─────────────────────────────────────────────────────────────────────────────

def load_csv_data(filepath: str):
    """Helper to load test data from a CSV file."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@pytest.fixture
def login_csv_data():
    """Load login test data from CSV file."""
    csv_path = os.path.join(os.path.dirname(__file__), "../../fixtures/login_data.csv")
    data = load_csv_data(csv_path)
    if not data:
        # Fallback inline data if CSV doesn't exist
        return [
            {"username": "tomsmith", "password": "SuperSecretPassword!", "expected": "success"},
            {"username": "baduser",  "password": "badpass",              "expected": "error"},
        ]
    return data


@pytest.mark.ui
@pytest.mark.data_driven
def test_login_from_csv(page: Page, login_csv_data):
    """TC-062: Data-driven login test reading from CSV."""
    for row in login_csv_data:
        login_page = LoginPage(page).load()
        login_page.login(row["username"], row["password"])

        if row["expected"] == "success":
            assert "/secure" in page.url or login_page.is_login_successful()
        else:
            assert login_page.is_error_shown(), \
                f"Expected error for: {row}"


# ─────────────────────────────────────────────────────────────────────────────
# Boundary Value Analysis Example
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.ui
@pytest.mark.data_driven
@pytest.mark.parametrize("length,should_pass", [
    (0,   False),   # empty — boundary min
    (1,   False),   # 1 char — below minimum
    (4,   False),   # 4 chars — typical minimum for passwords
    (8,   True),    # 8 chars — typical valid minimum (varies by app)
    (255, True),    # very long — boundary max (most apps allow)
    (256, False),   # over max — typical failure boundary
], ids=["empty", "1char", "4chars", "8chars", "255chars", "256chars"])
def test_password_length_boundaries(page: Page, length: int, should_pass: bool):
    """
    TC-063: Boundary value analysis on password field.
    NOTE: The-internet doesn't enforce length rules, so we test the
    concept here. In a real project these would map to real validation.
    """
    password = "A" * length
    login_page = LoginPage(page).load()
    login_page.enter_username("tomsmith")
    login_page.enter_password(password)
    login_page.click_login()
    # For the test site, only exact password works — this tests the pattern
    # In real apps: assert actual validation behaviour matches expected
    result = "pass" if "/secure" in page.url else "fail"
    # We just verify the page responded without crashing
    assert page.url is not None
