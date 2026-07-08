"""
pages package — Page Object Model
==================================
Centralised exports so tests can import cleanly:

    from pages import LoginPage, CheckboxPage, AlertsPage

instead of reaching into individual modules.
"""

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.secure_page import SecurePage
from pages.home_page import HomePage
from pages.checkbox_page import CheckboxPage
from pages.dropdown_page import DropdownPage
from pages.table_page import TablePage
from pages.dynamic_loading_page import DynamicLoadingPage
from pages.drag_drop_page import DragDropPage
from pages.alerts_page import AlertsPage

__all__ = [
    "BasePage",
    "LoginPage",
    "SecurePage",
    "HomePage",
    "CheckboxPage",
    "DropdownPage",
    "TablePage",
    "DynamicLoadingPage",
    "DragDropPage",
    "AlertsPage",
]
