"""
utils/wait_helpers.py — Advanced Wait Utilities
=================================================
Playwright's auto-wait handles 90% of cases.
These utilities cover the remaining 10%:
  - Polling for custom conditions
  - Waiting for JS variables
  - Waiting for element counts to stabilise
  - Retry wrappers for flaky external dependencies
"""

import time
import logging
from typing import Callable, Any
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


def wait_until(
    condition: Callable[[], bool],
    timeout: float = 10.0,
    poll_interval: float = 0.5,
    message: str = "Condition not met within timeout"
) -> None:
    """
    Poll a callable until it returns True or timeout expires.

    Use when Playwright's built-in waits don't cover your condition.
    Example: waiting for a Python variable to change, or a DB to update.

    Args:
        condition:     A callable that returns True when the wait is done.
        timeout:       Maximum seconds to wait.
        poll_interval: Seconds between polls.
        message:       Error message if timeout reached.

    Usage:
        wait_until(lambda: len(page.locator('.item').all()) > 5)
        wait_until(lambda: api.get('/status').json()['ready'] == True)
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if condition():
                return
        except Exception as e:
            logger.debug(f"wait_until condition raised: {e}")
        time.sleep(poll_interval)
    raise TimeoutError(f"{message} (after {timeout}s)")


def wait_for_js_variable(page: Page, variable_name: str, timeout: float = 10.0) -> Any:
    """
    Wait for a JavaScript variable to be defined and truthy.
    Useful when pages set window.appReady = true after async init.

    Usage:
        wait_for_js_variable(page, 'window.appReady')
        wait_for_js_variable(page, 'window.dataLayer.length > 0')
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = page.evaluate(f"() => {{ try {{ return {variable_name}; }} catch(e) {{ return null; }} }}")
        if result:
            return result
        time.sleep(0.3)
    raise TimeoutError(f"JS variable '{variable_name}' never became truthy within {timeout}s")


def wait_for_count_stable(locator: Locator, timeout: float = 5.0, stable_for: float = 0.5) -> int:
    """
    Wait until the count of matching elements stops changing.
    Useful after AJAX-loaded lists where items appear one by one.

    Returns the stable element count.
    """
    deadline     = time.time() + timeout
    last_count   = -1
    stable_since = None

    while time.time() < deadline:
        current_count = locator.count()
        if current_count == last_count:
            if stable_since is None:
                stable_since = time.time()
            elif time.time() - stable_since >= stable_for:
                return current_count
        else:
            last_count   = current_count
            stable_since = None
        time.sleep(0.2)

    raise TimeoutError(f"Element count never stabilised within {timeout}s. Last count: {last_count}")


def retry(
    func: Callable,
    retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """
    Retry a function on failure.
    Useful for actions that interact with flaky external services.

    Usage:
        result = retry(lambda: api.get('/flaky-endpoint').json(), retries=3)
    """
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            logger.warning(f"Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    raise last_exception


def wait_for_network_idle(page: Page, timeout: int = 15_000):
    """
    Explicit wrapper around wait_for_load_state('networkidle').
    More readable in test code than the raw call.
    """
    page.wait_for_load_state("networkidle", timeout=timeout)


def wait_for_no_spinner(page: Page, spinner_selector: str = ".spinner, .loading, #loading",
                        timeout: int = 15_000):
    """
    Wait for a loading spinner to disappear.
    Safe to call even if no spinner is present (catches timeout gracefully).
    """
    try:
        locator = page.locator(spinner_selector).first
        if locator.is_visible():
            locator.wait_for(state="hidden", timeout=timeout)
    except PlaywrightTimeoutError:
        logger.warning(f"Spinner '{spinner_selector}' still visible after {timeout}ms — continuing")
    except Exception:
        pass  # Spinner not found — that's fine
