"""
pages/alerts_page.py — JavaScript Alerts Page Object
======================================================
JS Alerts must be handled BEFORE clicking the button that triggers them.
Playwright uses page.on("dialog", ...) or page.once("dialog", ...).
"""

from playwright.sync_api import Page
from pages.base_page import BasePage


class AlertsPage(BasePage):
    """Handles JS Alerts, Confirms, and Prompts."""

    JS_ALERT_BTN   = "button[onclick='jsAlert()']"
    JS_CONFIRM_BTN = "button[onclick='jsConfirm()']"
    JS_PROMPT_BTN  = "button[onclick='jsPrompt()']"
    RESULT_TEXT    = "#result"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/javascript_alerts")
        return self

    def accept_alert(self) -> str:
        """Click the JS Alert button, accept it, return the result text."""
        self.handle_dialog(action="accept")
        self.click(self.JS_ALERT_BTN)
        return self.get_text(self.RESULT_TEXT)

    def accept_confirm(self) -> str:
        self.handle_dialog(action="accept")
        self.click(self.JS_CONFIRM_BTN)
        return self.get_text(self.RESULT_TEXT)

    def dismiss_confirm(self) -> str:
        self.handle_dialog(action="dismiss")
        self.click(self.JS_CONFIRM_BTN)
        return self.get_text(self.RESULT_TEXT)

    def fill_prompt(self, text: str) -> str:
        self.handle_dialog(action="accept", prompt_text=text)
        self.click(self.JS_PROMPT_BTN)
        return self.get_text(self.RESULT_TEXT)
