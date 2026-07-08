"""
pages/base_page.py — Base Page Object
=======================================
Every page object inherits from this class.

Why a Base Page?
  - Centralises common Playwright interactions (click, fill, wait, etc.)
  - Adds implicit retry logic and better error messages
  - Makes page objects thinner (less repeated boilerplate)
  - Easy to swap out Playwright for another driver in future without
    touching every individual page object
"""

import re
from playwright.sync_api import Page, expect, Locator
import logging

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all Page Objects.

    Constructor always receives a `page` (Playwright Page) and optionally
    a `base_url`.  Subclasses call super().__init__(page).
    """

    def __init__(self, page: Page):
        self.page = page

    # ─── Navigation ──────────────────────────────────────────────────────────

    def navigate(self, path: str = ""):
        """
        Navigate to a path relative to base_url configured in the context.
        Example: self.navigate("/login")
        """
        logger.info(f"Navigating to: {path}")
        self.page.goto(path)
        self.page.wait_for_load_state("networkidle")

    def get_current_url(self) -> str:
        return self.page.url

    def get_title(self) -> str:
        return self.page.title()

    def go_back(self):
        self.page.go_back()

    def reload(self):
        self.page.reload()

    # ─── Element Interaction ─────────────────────────────────────────────────

    def click(self, locator: str | Locator, timeout: int = 10_000):
        """Click an element.  Accepts both CSS/XPath strings and Locator objects."""
        logger.info(f"Clicking: {locator}")
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.wait_for(state="visible", timeout=timeout)
        target.click()

    def fill(self, locator: str | Locator, text: str, clear_first: bool = True):
        """Fill an input field.  Clears existing content by default."""
        logger.info(f"Filling '{locator}' with: {text}")
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        if clear_first:
            target.clear()
        target.fill(text)

    def type_slowly(self, locator: str | Locator, text: str, delay: int = 50):
        """
        Simulates real keyboard input character by character.
        Useful for inputs with autocomplete or JS validation.
        """
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.type(text, delay=delay)

    def select_option(self, locator: str | Locator, value: str = None,
                      label: str = None, index: int = None):
        """Select a <select> dropdown option by value, label, or index."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        if value:
            target.select_option(value=value)
        elif label:
            target.select_option(label=label)
        elif index is not None:
            target.select_option(index=index)

    def check(self, locator: str | Locator):
        """Check a checkbox."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.check()

    def uncheck(self, locator: str | Locator):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.uncheck()

    def hover(self, locator: str | Locator):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.hover()

    def press_key(self, locator: str | Locator, key: str):
        """Press a keyboard key on an element. e.g., press_key('#search', 'Enter')"""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.press(key)

    def upload_file(self, locator: str | Locator, file_path: str):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.set_input_files(file_path)

    def drag_and_drop(self, source: str | Locator, target: str | Locator):
        src = self.page.locator(source) if isinstance(source, str) else source
        tgt = self.page.locator(target) if isinstance(target, str) else target
        src.drag_to(tgt)

    # ─── Reading Values ───────────────────────────────────────────────────────

    def get_text(self, locator: str | Locator) -> str:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.inner_text()

    def get_input_value(self, locator: str | Locator) -> str:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.input_value()

    def get_attribute(self, locator: str | Locator, attribute: str) -> str:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.get_attribute(attribute)

    def is_visible(self, locator: str | Locator) -> bool:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.is_visible()

    def is_enabled(self, locator: str | Locator) -> bool:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.is_enabled()

    def is_checked(self, locator: str | Locator) -> bool:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.is_checked()

    def count_elements(self, locator: str | Locator) -> int:
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.count()

    # ─── Waits ────────────────────────────────────────────────────────────────

    def wait_for_element(self, locator: str | Locator, state: str = "visible",
                         timeout: int = 10_000):
        """
        Wait for an element to reach a specific state.
        state options: "visible" | "hidden" | "attached" | "detached"
        """
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.wait_for(state=state, timeout=timeout)

    def wait_for_url(self, url_pattern: str, timeout: int = 15_000):
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def wait_for_load_state(self, state: str = "networkidle"):
        """
        state options:
          "load"        — window.onload fired
          "domcontentloaded" — DOMContentLoaded fired
          "networkidle" — no network connections for 500ms  ← most reliable
        """
        self.page.wait_for_load_state(state)

    def wait_for_response(self, url_pattern: str, timeout: int = 15_000):
        """Wait for a specific network response (useful for API calls in UI tests)."""
        with self.page.expect_response(url_pattern, timeout=timeout) as response_info:
            pass
        return response_info.value

    # ─── Assertions (via Playwright's expect) ────────────────────────────────

    def assert_visible(self, locator: str | Locator, timeout: int = 10_000):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        expect(target).to_be_visible(timeout=timeout)

    def assert_text(self, locator: str | Locator, expected_text: str):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        expect(target).to_have_text(expected_text)

    def assert_contains_text(self, locator: str | Locator, text: str):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        expect(target).to_contain_text(text)

    def assert_url_contains(self, url_part: str):
        expect(self.page).to_have_url(re.compile(re.escape(url_part)))

    def assert_title(self, expected_title: str):
        expect(self.page).to_have_title(expected_title)

    # ─── JavaScript Execution ────────────────────────────────────────────────

    def execute_script(self, script: str, *args):
        """Run arbitrary JavaScript in the browser context."""
        return self.page.evaluate(script, *args)

    def scroll_into_view(self, locator: str | Locator):
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        target.scroll_into_view_if_needed()

    def scroll_to_bottom(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # ─── Screenshots ─────────────────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot", full_page: bool = True):
        import os
        os.makedirs("screenshots", exist_ok=True)
        path = f"screenshots/{name}.png"
        self.page.screenshot(path=path, full_page=full_page)
        logger.info(f"Screenshot saved: {path}")
        return path

    # ─── Dialogs ─────────────────────────────────────────────────────────────

    def handle_dialog(self, action: str = "accept", prompt_text: str = None):
        """
        Register a one-time dialog handler.
        Must be called BEFORE the action that triggers the dialog.
        action: "accept" | "dismiss"
        """
        def _handler(dialog):
            if action == "accept":
                dialog.accept(prompt_text) if prompt_text else dialog.accept()
            else:
                dialog.dismiss()
        self.page.once("dialog", _handler)

    # ─── Frame Handling ──────────────────────────────────────────────────────

    def get_frame(self, frame_name: str = None, url: str = None):
        """Switch to an iframe by name or URL."""
        if frame_name:
            return self.page.frame(name=frame_name)
        if url:
            return self.page.frame(url=url)

    def get_frame_locator(self, iframe_selector: str):
        """Use FrameLocator for interacting with elements inside an iframe."""
        return self.page.frame_locator(iframe_selector)
