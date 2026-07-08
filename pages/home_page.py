"""
pages/home_page.py — Home / Landing Page Object
=================================================
The landing page that lists all available examples.
"""

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class HomePage(BasePage):
    """Landing page — lists all available examples."""

    PAGE_HEADING  = "h1.heading"
    EXAMPLE_LINKS = "ul li a"

    def __init__(self, page: Page):
        super().__init__(page)

    def load(self):
        self.navigate("/")
        return self

    def get_heading(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def get_all_example_links(self) -> list[str]:
        """Returns the text of every example link on the home page."""
        links = self.page.locator(self.EXAMPLE_LINKS)
        return links.all_inner_texts()

    def navigate_to_example(self, link_text: str):
        """Click a specific example by its link text."""
        self.page.get_by_role("link", name=link_text).click()
        self.wait_for_load_state("domcontentloaded")
        return self

    def assert_loaded(self):
        expect(self.page).to_have_url("https://the-internet.herokuapp.com/")
        self.assert_visible(self.PAGE_HEADING)
