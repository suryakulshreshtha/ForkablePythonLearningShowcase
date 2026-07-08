# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] — Project reorganisation

### Changed
- Split `advanced_pages.py` into three feature-focused page objects:
  `dynamic_loading_page.py`, `drag_drop_page.py`, `alerts_page.py`.
- Split `form_pages.py` into four feature-focused page objects:
  `home_page.py`, `checkbox_page.py`, `dropdown_page.py`, `table_page.py`.
- `pages/__init__.py` now exports every page object for clean imports
  (`from pages import LoginPage`).
- Moved `COURSE_NOTES.md` into `docs/`.
- Moved the publish scripts into `scripts/`.

### Added
- `LICENSE` (MIT).
- `CHANGELOG.md` (this file).
- GitHub issue and pull-request templates under `.github/`.

## [1.0.1] — CI stabilisation

### Fixed
- `to_have_url()` assertions failed when a `base_url` was configured on the
  browser context, because Playwright prepended the base URL to the glob
  pattern. Replaced glob patterns with `re.compile(...)` regexes across all
  page objects and tests.
- Hardened `logout()` and `assert_on_secure_page()` to wait for navigation
  before asserting, removing a race condition on slower CI runners.

### Changed
- Bumped GitHub Actions to versions that run on Node.js 24
  (`checkout@v5`, `setup-python@v6`, `upload-artifact@v5`).
- Consolidated browser installation to `playwright install --with-deps`.
- Added `pytest-timeout` to silence the unknown-config-option warning.

## [1.0.0] — Initial release

### Added
- Playwright + pytest automation framework with 62 tests.
- Page Object Model with a shared `BasePage`.
- UI, API, E2E, and component test suites.
- Session-scoped browser fixture, function-scoped context/page isolation.
- Auth-state reuse (login once per suite).
- Screenshot-on-failure hook.
- Data-driven tests (parametrize, CSV, JSON).
- GitHub Actions CI with smoke, regression, and API jobs.
- HTML reporting via pytest-html.
