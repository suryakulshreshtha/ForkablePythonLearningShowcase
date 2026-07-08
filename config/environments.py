"""
config/environments.py — Environment Configuration Manager
============================================================
Centralises all environment-specific settings.
Instead of scattered os.getenv() calls across the codebase,
everything lives here and is accessed via get_config().

Usage in fixtures (conftest.py):
    from config.environments import get_config
    config = get_config("staging")
    base_url = config.base_url
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class EnvironmentConfig:
    name:          str
    base_url:      str
    api_base_url:  str
    username:      str
    password:      str
    headless:      bool = True
    slow_mo:       int  = 0
    timeout:       int  = 10_000
    nav_timeout:   int  = 30_000


# ── Environment definitions ───────────────────────────────────────────────────

ENVIRONMENTS = {
    "dev": EnvironmentConfig(
        name         = "dev",
        base_url     = os.getenv("DEV_URL",     "https://the-internet.herokuapp.com"),
        api_base_url = os.getenv("DEV_API_URL", "https://jsonplaceholder.typicode.com"),
        username     = os.getenv("DEV_USERNAME", "tomsmith"),
        password     = os.getenv("DEV_PASSWORD", "SuperSecretPassword!"),
        headless     = True,
        slow_mo      = 0,
    ),
    "staging": EnvironmentConfig(
        name         = "staging",
        base_url     = os.getenv("STAGING_URL",     "https://the-internet.herokuapp.com"),
        api_base_url = os.getenv("STAGING_API_URL", "https://jsonplaceholder.typicode.com"),
        username     = os.getenv("TEST_USERNAME", "tomsmith"),
        password     = os.getenv("TEST_PASSWORD", "SuperSecretPassword!"),
        headless     = True,
        slow_mo      = 0,
    ),
    "prod": EnvironmentConfig(
        name         = "prod",
        base_url     = os.getenv("PROD_URL",     "https://the-internet.herokuapp.com"),
        api_base_url = os.getenv("PROD_API_URL", "https://jsonplaceholder.typicode.com"),
        username     = os.getenv("PROD_USERNAME", "tomsmith"),
        password     = os.getenv("PROD_PASSWORD", "SuperSecretPassword!"),
        headless     = True,
        slow_mo      = 0,
    ),
}


def get_config(env_name: str = None) -> EnvironmentConfig:
    """
    Returns the EnvironmentConfig for the given environment name.
    Falls back to ENV variable, then 'staging' as default.

    Example:
        config = get_config("staging")
        page.goto(config.base_url + "/login")
    """
    name = env_name or os.getenv("ENV", "staging")
    config = ENVIRONMENTS.get(name)
    if not config:
        valid = ", ".join(ENVIRONMENTS.keys())
        raise ValueError(f"Unknown environment '{name}'. Valid options: {valid}")
    return config
