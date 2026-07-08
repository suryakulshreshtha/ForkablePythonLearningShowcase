"""
conftest.py — Pytest Fixtures & Hooks
======================================
This is the most important file in a Playwright-pytest framework.
Fixtures defined here are automatically available to ALL test files
without any import — pytest discovers them automatically.

Key concepts covered:
  - Browser / BrowserContext / Page lifecycle management
  - Scope: session → module → class → function (default)
  - Custom CLI options via pytest_addoption
  - Screenshot-on-failure hook
  - Allure environment attachment
  - Base URL injection
"""

import os
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from dotenv import load_dotenv

# Load .env file (BASE_URL, credentials, etc.)
load_dotenv()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Custom CLI Options
# ─────────────────────────────────────────────────────────────────────────────

def pytest_addoption(parser):
    """
    Add custom command-line options to pytest.
    Usage examples:
        pytest --browser=firefox
        pytest --env=staging
        pytest --headless=false
    """
    parser.addoption(
        "--env",
        action="store",
        default="staging",
        help="Target environment: staging | prod | dev"
    )
    parser.addoption(
        "--browser-type",
        action="store",
        default="chromium",
        help="Browser to use: chromium | firefox | webkit"
    )
    parser.addoption(
        "--headless",
        action="store",
        default="true",
        help="Run headless: true | false"
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Configuration Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def env(request):
    """Returns the target environment string."""
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env):
    """
    Returns the base URL for the current environment.
    Maps env name → URL from environment variables or hardcoded fallbacks.
    """
    urls = {
        "dev":     os.getenv("DEV_URL",     "https://dev.example.com"),
        "staging": os.getenv("STAGING_URL", "https://the-internet.herokuapp.com"),
        "prod":    os.getenv("PROD_URL",    "https://the-internet.herokuapp.com"),
    }
    return urls.get(env, "https://the-internet.herokuapp.com")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Browser Lifecycle Fixtures (session-scoped for speed)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_type_name(request):
    return request.config.getoption("--browser-type")


@pytest.fixture(scope="session")
def is_headless(request):
    value = request.config.getoption("--headless")
    return value.lower() != "false"


@pytest.fixture(scope="session")
def playwright_instance():
    """
    Starts one Playwright instance for the entire test session.
    Using session scope prevents slow browser startup on every test.
    """
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, browser_type_name, is_headless) -> Browser:
    """
    Launches the browser once per session.
    slow_mo: adds a delay (ms) between actions — useful for demos/debugging.
    """
    browser_launchers = {
        "chromium": playwright_instance.chromium,
        "firefox":  playwright_instance.firefox,
        "webkit":   playwright_instance.webkit,
    }
    launcher = browser_launchers.get(browser_type_name, playwright_instance.chromium)

    browser_instance = launcher.launch(
        headless=is_headless,
        slow_mo=0,                        # change to 500 for slow-motion demo
        args=["--no-sandbox"] if browser_type_name == "chromium" else [],
    )
    yield browser_instance
    browser_instance.close()


@pytest.fixture(scope="function")
def context(browser, base_url) -> BrowserContext:
    """
    Creates a NEW isolated BrowserContext per test function.
    Each context = fresh cookies, localStorage, sessionStorage.
    This is the correct isolation level for most UI tests.
    """
    ctx = browser.new_context(
        base_url=base_url,
        viewport={"width": 1280, "height": 720},
        record_video_dir="reports/videos/" if os.getenv("RECORD_VIDEO") else None,
        ignore_https_errors=True,
    )
    ctx.set_default_timeout(10_000)       # 10 seconds global timeout
    ctx.set_default_navigation_timeout(30_000)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context) -> Page:
    """
    Opens a single tab (Page) per test inside the isolated context.
    This is what you'll inject into almost every test function.
    """
    p = context.new_page()
    yield p
    p.close()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Authenticated Page Fixture (reuses saved auth state)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def auth_state_path(tmp_path_factory):
    """Returns the path where login state (cookies + localStorage) is saved."""
    return str(tmp_path_factory.mktemp("auth") / "auth_state.json")


@pytest.fixture(scope="session")
def authenticated_context(browser, base_url, auth_state_path):
    """
    Logs in ONCE, saves auth state to disk, reuses for all tests that
    request this fixture.  This is playwright's recommended approach to
    avoid logging in before every single test.
    """
    ctx = browser.new_context(base_url=base_url, viewport={"width": 1280, "height": 720})
    pg  = ctx.new_page()

    # Perform login
    pg.goto("/login")
    pg.fill("#username", os.getenv("TEST_USERNAME", "admin"))
    pg.fill("#password", os.getenv("TEST_PASSWORD", "admin"))
    pg.click("button[type='submit']")
    pg.wait_for_url("**/secure")          # wait until redirected after login

    # Save session state so other tests can reuse it
    ctx.storage_state(path=auth_state_path)
    pg.close()
    ctx.close()

    # Return a fresh context that loads the saved auth state
    auth_ctx = browser.new_context(
        base_url=base_url,
        storage_state=auth_state_path,
        viewport={"width": 1280, "height": 720},
    )
    yield auth_ctx
    auth_ctx.close()


@pytest.fixture(scope="function")
def logged_in_page(authenticated_context) -> Page:
    """A page that is already authenticated. Use for tests that need login."""
    pg = authenticated_context.new_page()
    yield pg
    pg.close()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Hooks — Screenshot on Failure
# ─────────────────────────────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook that runs around each test phase (setup/call/teardown).
    We capture a screenshot when a test FAILS in the 'call' phase.
    """
    outcome = yield
    report  = outcome.get_result()

    if report.when == "call" and report.failed:
        # Try to get the 'page' fixture from the test item
        page_fixture = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if page_fixture:
            os.makedirs("screenshots", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name  = item.name.replace("/", "_").replace(" ", "_")
            path       = f"screenshots/FAIL_{safe_name}_{timestamp}.png"
            page_fixture.screenshot(path=path, full_page=True)
            print(f"\n📸 Screenshot saved: {path}")
