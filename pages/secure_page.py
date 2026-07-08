"""
pages/secure_page.py — Secure (Post-Login) Page Object
"""
import re
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class SecurePage(BasePage):

    PAGE_HEADING  = "h2"
    LOGOUT_BUTTON = "a[href='/logout']"
    WELCOME_MSG   = "#flash"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/secure")
        return self

    def logout(self):
        self.click(self.LOGOUT_BUTTON)
        # Wait for the redirect back to /login to complete before returning,
        # so downstream URL assertions don't race the navigation.
        self.page.wait_for_url(re.compile(r"/login$"), timeout=15_000)
        return self

    def get_heading(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def assert_on_secure_page(self):
        # Wait for navigation to settle first, then assert — avoids racing
        # the post-login redirect on slower CI runners.
        self.page.wait_for_url(re.compile(r"/secure$"), timeout=15_000)
        expect(self.page).to_have_url(re.compile(r"/secure$"))
        expect(self.page.locator(self.PAGE_HEADING)).to_contain_text("Secure Area")
