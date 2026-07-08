# 🎭 Playwright + Pytest Automation Testing — Master Notes
### Senior Automation Test Manager Perspective | Python | 2025

> **Target audience:** QA Engineers, SDETs, and Developers building a production-grade test automation framework.  
> **Test site used throughout:** `https://the-internet.herokuapp.com`

---

## TABLE OF CONTENTS

1. [Why Playwright over Selenium](#1-why-playwright-over-selenium)
2. [Environment Setup](#2-environment-setup)
3. [Playwright Core Concepts](#3-playwright-core-concepts)
4. [Pytest Fundamentals for Automation](#4-pytest-fundamentals-for-automation)
5. [Page Object Model (POM)](#5-page-object-model-pom)
6. [Locators — The Right Way](#6-locators--the-right-way)
7. [Waits and Synchronisation](#7-waits-and-synchronisation)
8. [UI Interactions — Complete Reference](#8-ui-interactions--complete-reference)
9. [API Testing with Playwright](#9-api-testing-with-playwright)
10. [Advanced Patterns](#10-advanced-patterns)
11. [Data-Driven Testing](#11-data-driven-testing)
12. [Parallel Execution](#12-parallel-execution)
13. [Reporting](#13-reporting)
14. [CI/CD Integration](#14-cicd-integration)
15. [Best Practices & Anti-Patterns](#15-best-practices--anti-patterns)

---

## 1. Why Playwright over Selenium

| Feature | Playwright | Selenium |
|---|---|---|
| Auto-wait | ✅ Built-in (no explicit waits needed) | ❌ Manual `WebDriverWait` required |
| Browser support | Chromium, Firefox, WebKit (Safari) | Chrome, Firefox, Edge, Safari |
| Speed | 🚀 Fast (direct protocol) | 🐢 Slower (JSON Wire / W3C) |
| Network interception | ✅ Native | ❌ Need extra libraries |
| API testing | ✅ Built-in `APIRequestContext` | ❌ Not supported |
| iFrame handling | ✅ `frame_locator()` — elegant | ❌ `switch_to.frame()` — brittle |
| Multiple tabs | ✅ `context.expect_page()` | ⚠️ Complex `window_handles` dance |
| Auth state reuse | ✅ `storage_state` — login once | ❌ Must re-login every context |
| Setup cost | `pip install playwright` + `playwright install` | Driver management nightmare |
| Mobile emulation | ✅ Built-in device descriptors | ⚠️ Limited |

**Key architectural insight:** Playwright communicates with browsers over the Chrome DevTools Protocol (CDP) directly — this is why it's faster and more reliable than Selenium's JSON Wire Protocol.

---

## 2. Environment Setup

### Prerequisites
```bash
# Verify Python 3.9+
python --version

# Create a virtual environment (ALWAYS work in a venv)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Install Everything
```bash
pip install playwright pytest pytest-playwright pytest-html
playwright install              # installs Chromium, Firefox, WebKit
playwright install-deps         # installs OS-level dependencies (Linux)
```

### Verify Installation
```bash
playwright --version
pytest --version
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### First Playwright Script (without pytest)
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)   # headless=False → see the browser
    page = browser.new_page()
    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")
    page.wait_for_url("**/secure")
    print(page.title())
    browser.close()
```

---

## 3. Playwright Core Concepts

### The Object Hierarchy
```
Playwright
  └── Browser          (one per browser type: Chromium / Firefox / WebKit)
        └── BrowserContext   (isolated session — like an incognito window)
              └── Page         (single browser tab)
                    └── Locator  (element reference — lazy, not yet found)
```

### Sync vs Async API
```python
# SYNC (use this for pytest — simpler, sequential)
from playwright.sync_api import sync_playwright, Page

# ASYNC (use this for async frameworks — FastAPI, asyncio)
from playwright.async_api import async_playwright, Page
```

### BrowserContext — The Key Isolation Unit
```python
# Each context = completely isolated browser session
# Perfect for parallel tests — no cookie/localStorage contamination

context1 = browser.new_context()   # User A session
context2 = browser.new_context()   # User B session
# They share nothing — even on the same browser instance
```

### Auth State Reuse (login once per suite)
```python
# Save logged-in state to disk
context.storage_state(path="auth_state.json")

# Load it into a new context — no re-login needed!
new_context = browser.new_context(storage_state="auth_state.json")
```

---

## 4. Pytest Fundamentals for Automation

### conftest.py — The Backbone
`conftest.py` is a special pytest file. Fixtures defined here are available to ALL tests in the same directory and subdirectories **automatically** — no import needed.

```
project/
├── conftest.py           ← session/cross-suite fixtures
├── tests/
│   ├── conftest.py       ← suite-level fixtures (overrides parent if same name)
│   ├── ui/
│   │   ├── conftest.py   ← UI-specific fixtures
│   │   └── test_login.py
│   └── api/
│       └── test_api.py
```

### Fixture Scopes (most important concept!)
```python
# FUNCTION (default) — fresh for every single test
@pytest.fixture(scope="function")
def page(context):
    p = context.new_page()
    yield p
    p.close()

# CLASS — shared across all tests in a class
@pytest.fixture(scope="class")
def setup_class_data():
    return {"key": "value"}

# MODULE — shared across all tests in a file
@pytest.fixture(scope="module")
def api_context(playwright):
    ctx = playwright.request.new_context(base_url="...")
    yield ctx
    ctx.dispose()

# SESSION — created once for the entire test run (most expensive, most reuse)
@pytest.fixture(scope="session")
def browser(playwright_instance):
    b = playwright_instance.chromium.launch()
    yield b
    b.close()
```

**Rule of thumb:**
- `browser` → session scope (slow to start, expensive)  
- `context` → function scope (provides isolation between tests)  
- `page` → function scope (fresh tab per test)
- Static config/data → session scope

### Fixtures with yield (setup + teardown)
```python
@pytest.fixture
def page(context):
    # === SETUP ===
    p = context.new_page()
    
    yield p              # <-- test runs here; p is injected
    
    # === TEARDOWN (always runs, even on test failure) ===
    p.close()
```

### Custom CLI Options
```python
# In conftest.py:
def pytest_addoption(parser):
    parser.addoption("--env", default="staging")
    parser.addoption("--browser-type", default="chromium")

# In a fixture:
@pytest.fixture
def env(request):
    return request.config.getoption("--env")
```

```bash
# Run with custom options:
pytest --env=prod --browser-type=firefox -m smoke
```

### Markers
```python
# Declare in pytest.ini:
# markers =
#     smoke: fast critical path tests
#     regression: full suite
#     api: API tests

# Apply to test:
@pytest.mark.smoke
@pytest.mark.parametrize("url", ["/login", "/signup"])
def test_pages_load(page, url):
    page.goto(url)
    assert page.title() != ""
```

```bash
# Run only smoke tests:
pytest -m smoke

# Run smoke OR api:
pytest -m "smoke or api"

# Run regression but NOT slow:
pytest -m "regression and not slow"
```

### Parametrize — Data-Driven in One Decorator
```python
@pytest.mark.parametrize("username, password, expected", [
    ("tomsmith", "SuperSecretPassword!", "success"),
    ("baduser",  "badpass",              "error"),
], ids=["valid-creds", "invalid-creds"])   # ids make reports readable
def test_login(page, username, password, expected):
    ...
```

### Hooks — Intercept Test Lifecycle
```python
# Screenshot on failure — goes in conftest.py
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report  = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            page.screenshot(path=f"screenshots/FAIL_{item.name}.png")
```

---

## 5. Page Object Model (POM)

### Why POM?
| Without POM | With POM |
|---|---|
| Selectors scattered everywhere | Selectors in one place |
| Change a selector → update 20 test files | Change a selector → update 1 page file |
| Tests are hard to read | Tests read like user stories |
| No reuse | Methods reused across tests |

### POM Structure
```python
# pages/login_page.py
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

class LoginPage(BasePage):
    # 1. Locators as class-level constants
    USERNAME  = "#username"
    PASSWORD  = "#password"
    SUBMIT    = "button[type='submit']"
    FLASH     = "#flash"

    def __init__(self, page: Page):
        super().__init__(page)

    # 2. Navigation method returns self (enables chaining)
    def load(self):
        self.navigate("/login")
        return self

    # 3. Action methods — one per user action
    def login(self, username: str, password: str):
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.SUBMIT)
        return self

    # 4. Assertion methods — wrap playwright's expect()
    def assert_success(self):
        expect(self.page).to_have_url("**/secure")
```

```python
# test_login.py — reads like English
def test_valid_login(page):
    LoginPage(page).load().login("tomsmith", "SuperSecretPassword!").assert_success()
```

### Base Page Pattern
```python
# pages/base_page.py — shared actions all pages inherit
class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def click(self, selector):
        self.page.locator(selector).click()

    def fill(self, selector, text):
        self.page.locator(selector).fill(text)

    def navigate(self, path):
        self.page.goto(path)
        self.page.wait_for_load_state("networkidle")
```

---

## 6. Locators — The Right Way

### Priority Order (most to least stable)
```python
# 1. BEST: data-testid (purpose-built for testing, never changes with design)
page.get_by_test_id("login-button")

# 2. ARIA Role (semantic, matches how users & screen readers see the page)
page.get_by_role("button", name="Sign In")
page.get_by_role("textbox", name="Username")
page.get_by_role("link", name="Forgot password?")

# 3. Label text (great for form inputs)
page.get_by_label("Email address")

# 4. Placeholder text
page.get_by_placeholder("Enter your email")

# 5. Visible text
page.get_by_text("Welcome back")

# 6. CSS selector (widely used, acceptable)
page.locator("#username")
page.locator(".login-form input[type='password']")

# 7. XPath (avoid unless CSS can't reach it)
page.locator("//button[@type='submit']")
```

### Chaining Locators (narrow down scope)
```python
# Find a button inside a specific form
form    = page.locator("form#login-form")
button  = form.locator("button[type='submit']")
button.click()

# Or in one line:
page.locator("form#login-form").locator("button[type='submit']").click()
```

### Working with Lists of Elements
```python
items = page.locator(".product-card")

# Count
count = items.count()

# Iterate
for i in range(count):
    print(items.nth(i).inner_text())

# First / Last
items.first.click()
items.last.inner_text()

# Filter by text
items.filter(has_text="Laptop").click()

# Get all texts at once
texts = items.all_inner_texts()   # returns list of strings
```

### Locator Assertions (playwright's expect — auto-retry)
```python
from playwright.sync_api import expect

# Playwright retries these assertions automatically for up to the timeout
# No flakiness from race conditions!

expect(locator).to_be_visible()
expect(locator).to_be_hidden()
expect(locator).to_be_enabled()
expect(locator).to_be_disabled()
expect(locator).to_be_checked()
expect(locator).to_have_text("exact text")
expect(locator).to_contain_text("partial text")
expect(locator).to_have_value("input value")
expect(locator).to_have_count(5)
expect(locator).to_have_attribute("class", "active")
expect(locator).to_have_class("btn-primary")
expect(page).to_have_url("https://example.com/dashboard")
expect(page).to_have_title("Dashboard")
```

---

## 7. Waits and Synchronisation

### Playwright's Auto-Wait (the game changer)
Playwright automatically waits for elements to be:
- Attached to DOM
- Visible
- Stable (not animating)
- Enabled
- Not obscured

**You almost never need `time.sleep()` in Playwright.**

```python
# BAD — never do this
import time
time.sleep(3)
page.click("#submit")

# GOOD — Playwright handles this for you
page.click("#submit")   # automatically waits for the element to be ready
```

### When You DO Need Explicit Waits

```python
# Wait for a specific element state
page.locator("#loading-spinner").wait_for(state="hidden")
page.locator("#results-table").wait_for(state="visible")

# Wait for network to settle
page.wait_for_load_state("networkidle")

# Wait for URL change (after form submission / redirect)
page.wait_for_url("**/dashboard")
page.wait_for_url("https://app.com/dashboard", timeout=15_000)

# Wait for a specific network request/response
with page.expect_response("**/api/users") as response_info:
    page.click("#load-users")
response = response_info.value
assert response.status == 200

# Wait for a navigation to complete
with page.expect_navigation():
    page.click("a.next-page")
```

### Setting Timeouts
```python
# Global timeout for all actions/assertions (in context)
context.set_default_timeout(10_000)           # 10 seconds
context.set_default_navigation_timeout(30_000) # 30 seconds for page loads

# Per-action timeout override
page.locator("#slow-element").wait_for(state="visible", timeout=20_000)
page.click("#button", timeout=5_000)
expect(locator).to_be_visible(timeout=15_000)
```

---

## 8. UI Interactions — Complete Reference

### Forms
```python
# Text input
page.fill("#email", "user@example.com")
page.type("#email", "user@example.com", delay=50)  # simulates typing

# Clear and refill
page.locator("#email").clear()
page.locator("#email").fill("new@example.com")

# Checkbox
page.check("#agree-terms")
page.uncheck("#newsletter")
expect(page.locator("#agree-terms")).to_be_checked()

# Radio button
page.locator("input[value='monthly']").check()

# Select dropdown
page.select_option("#country", value="IN")
page.select_option("#country", label="India")
page.select_option("#country", index=2)
page.select_option("#multi-select", ["option1", "option2"])  # multi-select

# File upload
page.locator("#file-input").set_input_files("/path/to/file.pdf")
page.locator("#file-input").set_input_files(["file1.pdf", "file2.pdf"])  # multiple
```

### Clicks and Keyboard
```python
page.click("#button")
page.dblclick("#item")
page.click("#button", button="right")      # right-click
page.click("#button", modifiers=["Shift"]) # Shift+Click
page.click("#input", click_count=3)        # triple-click (selects all text)

# Keyboard
page.keyboard.press("Enter")
page.keyboard.press("Control+A")
page.keyboard.press("Tab")
page.keyboard.type("Hello World")

# Press on specific element
page.locator("#search").press("Enter")
```

### Scrolling
```python
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # scroll to bottom
page.locator("#element").scroll_into_view_if_needed()
page.mouse.wheel(0, 300)  # scroll 300px down
```

### Hover
```python
page.hover("#menu-item")
page.locator("#dropdown-trigger").hover()
```

### Drag and Drop
```python
page.drag_and_drop("#source", "#target")
# Or with locators:
page.locator("#source").drag_to(page.locator("#target"))
```

### Frames (iFrames)
```python
# Modern approach: FrameLocator (preferred)
frame = page.frame_locator("#my-iframe")
frame.locator("#inner-button").click()

# Legacy approach: switch to frame
frame = page.frame(name="my-frame")
frame.locator("#inner-button").click()
```

### Multiple Tabs / Windows
```python
# Handle a link that opens a new tab
with context.expect_page() as new_page_info:
    page.click("a[target='_blank']")
new_tab = new_page_info.value
new_tab.wait_for_load_state()
print(new_tab.title())

# Close new tab and switch back
new_tab.close()
# Original page is still `page`
```

### JS Alerts / Confirms / Prompts
```python
# CRITICAL: Register handler BEFORE the action that triggers it
page.on("dialog", lambda d: d.accept())
page.click("#alert-trigger")

# One-time handler with specific response
page.once("dialog", lambda d: d.accept("my prompt input"))
page.click("#prompt-trigger")

# Dismiss
page.once("dialog", lambda d: d.dismiss())
page.click("#confirm-trigger")
```

---

## 9. API Testing with Playwright

### Standalone API Context (no browser)
```python
@pytest.fixture(scope="module")
def api(playwright):
    ctx = playwright.request.new_context(
        base_url="https://api.example.com",
        extra_http_headers={"Authorization": f"Bearer {TOKEN}"}
    )
    yield ctx
    ctx.dispose()
```

### CRUD Operations
```python
# GET
response = api.get("/users/1")
assert response.status == 200
user = response.json()

# POST
response = api.post("/users", data={"name": "Surya", "email": "s@example.com"})
assert response.status == 201

# PUT (full replace)
response = api.put("/users/1", data={"name": "Updated", "email": "u@example.com"})

# PATCH (partial update)
response = api.patch("/users/1", data={"name": "Patched Name"})

# DELETE
response = api.delete("/users/1")
assert response.status in (200, 204)
```

### Response Inspection
```python
response = api.get("/products")

# Status
response.status          # 200
response.ok              # True if 200-299
response.status_text     # "OK"

# Headers
response.headers["content-type"]

# Body
response.json()          # parse as JSON
response.text()          # raw text body
response.body()          # bytes

# Request details
response.url
response.request.method
response.request.headers
```

### Network Interception (mocking)
```python
# Block all requests to a domain
page.route("**/ads.example.com/**", lambda route: route.abort())

# Return a mock response
page.route("**/api/users", lambda route: route.fulfill(
    status=200,
    content_type="application/json",
    body='[{"id": 1, "name": "Mock User"}]'
))

# Intercept and modify a real response
def modify(route):
    response = route.fetch()
    json_body = response.json()
    json_body["extra_field"] = "injected"
    route.fulfill(response=response, body=json.dumps(json_body))

page.route("**/api/data", modify)
```

---

## 10. Advanced Patterns

### Screenshot on Failure (hook in conftest.py)
```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            page.screenshot(path=f"screenshots/FAIL_{item.name}.png", full_page=True)
```

### Video Recording
```python
context = browser.new_context(
    record_video_dir="reports/videos/",
    record_video_size={"width": 1280, "height": 720}
)
# Video is saved when context is closed
context.close()
```

### Mobile Emulation
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices["iPhone 13"]
    browser = p.webkit.launch()
    context = browser.new_context(**iphone)  # unpacks device config
    page = context.new_page()
    page.goto("https://example.com")
    # Page renders as it would on an iPhone 13
```

### Geo-Location, Permissions
```python
context = browser.new_context(
    geolocation={"latitude": 28.6139, "longitude": 77.2090},  # New Delhi
    permissions=["geolocation"]
)
```

### Tracing (built-in debugging)
```python
context.tracing.start(screenshots=True, snapshots=True)
# ... run tests ...
context.tracing.stop(path="trace.zip")

# Open in Playwright Trace Viewer:
# playwright show-trace trace.zip
```

### Cross-Browser Testing
```python
@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
def test_cross_browser(browser_name):
    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch()
        page = browser.new_page()
        page.goto("https://example.com")
        assert "Example Domain" in page.title()
        browser.close()
```

### Soft Assertions (don't fail fast)
```python
# All assertions run even if one fails — collect all failures
from playwright.sync_api import expect

# Use expect() — it collects failures by default in some configs
# Or use pytest-check for soft assertions:
import pytest_check as check

def test_multiple_assertions(page):
    page.goto("/profile")
    check.equal(page.locator("h1").inner_text(), "Profile")   # won't stop test
    check.is_true(page.locator(".avatar").is_visible())        # won't stop test
    check.equal(page.locator(".email").inner_text(), "user@example.com")
    # All failures reported at the end
```

---

## 11. Data-Driven Testing

### Three Approaches

#### 1. Inline `@pytest.mark.parametrize`
```python
@pytest.mark.parametrize("username, password, expected", [
    ("tomsmith", "SuperSecretPassword!", "success"),
    ("baduser",  "badpass",              "error"),
], ids=["valid", "invalid"])
def test_login(page, username, password, expected):
    ...
```

#### 2. CSV File
```python
import csv

def load_test_data(filepath):
    with open(filepath) as f:
        return list(csv.DictReader(f))

@pytest.fixture
def login_data():
    return load_test_data("fixtures/login_data.csv")

def test_login_csv(page, login_data):
    for row in login_data:
        LoginPage(page).load().login(row["username"], row["password"])
        ...
```

#### 3. JSON File
```python
import json

@pytest.fixture
def user_data():
    with open("fixtures/users.json") as f:
        return json.load(f)
```

---

## 12. Parallel Execution

```bash
# Install
pip install pytest-xdist

# Run tests in parallel using all CPU cores
pytest -n auto

# Run with specific number of workers
pytest -n 4

# Distribute by test file (default: by test function)
pytest -n 4 --dist=loadfile
```

**Important:** Parallel tests must be isolated. Each test must have its own `context` and `page`. Never share state between parallel tests.

```python
# GOOD — function-scoped context (each test gets its own)
@pytest.fixture(scope="function")
def context(browser):
    ctx = browser.new_context()
    yield ctx
    ctx.close()

# BAD — module-scoped context shared between parallel tests (race condition!)
@pytest.fixture(scope="module")
def context(browser):
    ...
```

---

## 13. Reporting

### HTML Report (pytest-html)
```bash
pytest --html=reports/report.html --self-contained-html
```

### Allure Report (professional, with screenshots)
```bash
pip install allure-pytest
pytest --alluredir=allure-results
allure serve allure-results          # opens in browser
allure generate allure-results -o allure-report  # static HTML
```

```python
import allure

@allure.feature("Authentication")
@allure.story("Login")
@allure.title("Valid login redirects to secure area")
@allure.severity(allure.severity_level.CRITICAL)
def test_valid_login(page):
    with allure.step("Navigate to login page"):
        page.goto("/login")
    with allure.step("Enter credentials"):
        page.fill("#username", "tomsmith")
        page.fill("#password", "SuperSecretPassword!")
    with allure.step("Click login"):
        page.click("button[type='submit']")
    with allure.step("Verify redirect"):
        assert "/secure" in page.url
```

---

## 14. CI/CD Integration

### GitHub Actions Key Concepts
```yaml
# .github/workflows/playwright-tests.yml
name: Playwright Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: playwright install chromium --with-deps
      - run: pytest -m smoke --html=reports/report.html
      - uses: actions/upload-artifact@v4
        if: always()           # upload report even on failure!
        with:
          name: test-report
          path: reports/
```

### GitHub Secrets for Credentials
```yaml
# In your workflow:
env:
  TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}

# Add in GitHub: Settings → Secrets → Actions → New repository secret
```

---

## 15. Best Practices & Anti-Patterns

### ✅ DO This

| Practice | Why |
|---|---|
| Use `data-testid` attributes | Stable selectors that survive UI redesigns |
| Session-scope the browser | Slow to start — reuse across tests |
| Function-scope the context | Fresh isolation per test |
| Login once, save auth state | 10x faster than re-logging in per test |
| Use `expect()` assertions | Auto-retries, better error messages |
| Screenshot on failure (hook) | Instant debugging of CI failures |
| Keep tests independent | Parallel execution, no order dependency |
| Use Page Objects | Maintainability, readability |
| Declare all markers in pytest.ini | Prevents `PytestUnknownMarkWarning` |
| Use `--strict-markers` in pytest.ini | Typo in marker name = test fails (caught early) |

### ❌ NEVER Do This

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `time.sleep(3)` | Flaky — either too slow or too fast | Use auto-wait or explicit `wait_for_*` |
| Raw selectors in test files | Breaks when UI changes | Use Page Objects |
| Shared mutable state between tests | Parallel failures, order dependency | Use function-scoped fixtures |
| Hardcoded credentials | Security risk | Use `.env` / CI secrets |
| Catching `Exception` broadly | Hides real failures | Catch specific exceptions |
| Re-logging in for every test | 10x slower | Save and reuse auth state |
| Running all tests as regression | Slow feedback | Tag and run by markers |
| Asserting with `assert` on network calls | Race condition | Use `page.expect_response()` |

### The Testing Pyramid
```
           /\
          /E2E\         ← 10%  Slow. Test critical user journeys only.
         /------\
        /  API   \      ← 30%  Fast. Test business logic at the API layer.
       /----------\
      /  UI Unit   \    ← 60%  Medium. Test individual UI components/pages.
     /--------------\
```

### Folder Structure for Scaling
```
ForkablePythonLearningShowcase/
├── .github/workflows/      # CI/CD pipeline
├── config/                 # environment configs
├── fixtures/               # test data (CSV, JSON)
├── pages/                  # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   └── ...
├── tests/
│   ├── ui/                 # browser-based tests
│   ├── api/                # API-only tests
│   └── e2e/                # end-to-end flows
├── utils/                  # helper functions
├── reports/                # generated (gitignored)
├── screenshots/            # generated (gitignored)
├── conftest.py             # global fixtures & hooks
├── pytest.ini              # pytest config
├── requirements.txt
└── .env.example
```
