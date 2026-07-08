"""
pages/login_page.py — Login Page Object
=========================================
Encapsulates ALL interactions with the login page.

POM Rule: Tests should never contain raw selectors.
           Every selector lives here, in the page object.
"""

import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LoginPage(BasePage):

    # ── Locators (defined as properties for readability) ─────────────────────
    # TIP: Use data-testid attributes in production apps — far more stable
    #      than CSS classes or XPath.

    USERNAME_INPUT  = "#username"
    PASSWORD_INPUT  = "#password"
    LOGIN_BUTTON    = "button[type='submit']"
    FLASH_MESSAGE   = "#flash"
    ERROR_MESSAGE   = "#flash.error"
    SUCCESS_MESSAGE = "#flash.success"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        """Navigate to the login page."""
        self.navigate("/login")
        return self                       # enables method chaining: LoginPage(page).load().login(...)

    def enter_username(self, username: str):
        self.fill(self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str):
        self.fill(self.PASSWORD_INPUT, password)
        return self

    def click_login(self):
        self.click(self.LOGIN_BUTTON)
        return self

    def login(self, username: str, password: str):
        """
        Complete login flow in one call.
        Returns self so tests can chain assertions.
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self

    def get_flash_message(self) -> str:
        return self.get_text(self.FLASH_MESSAGE)

    def is_login_successful(self) -> bool:
        """Returns True if the success flash banner is visible."""
        return self.is_visible(self.SUCCESS_MESSAGE)

    def is_error_shown(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)

    def assert_login_success(self):
        expect(self.page.locator(self.SUCCESS_MESSAGE)).to_be_visible()
        expect(self.page).to_have_url(re.compile(r"/secure$"))

    def assert_login_error(self, expected_message: str = None):
        expect(self.page.locator(self.ERROR_MESSAGE)).to_be_visible()
        if expected_message:
            expect(self.page.locator(self.FLASH_MESSAGE)).to_contain_text(expected_message)
