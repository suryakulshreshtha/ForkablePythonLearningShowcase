"""
utils/helpers.py — Reusable Test Utilities
============================================
Standalone helper functions used across multiple tests.
Keep these STATELESS (no page/browser dependency) — they work
on data, not on browser objects.
"""

import os
import json
import csv
import random
import string
from datetime import datetime
from faker import Faker

faker = Faker()


# ─────────────────────────────────────────────────────────────────────────────
# Random Data Generators
# ─────────────────────────────────────────────────────────────────────────────

def random_email() -> str:
    """Generate a unique random email address."""
    return faker.email()


def random_name() -> str:
    return faker.name()


def random_phone() -> str:
    return faker.phone_number()


def random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters, k=length))


def random_password(length: int = 12) -> str:
    """Generate a strong random password."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=length))


def timestamp() -> str:
    """Return current timestamp as a string. Useful for unique test data."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


# ─────────────────────────────────────────────────────────────────────────────
# File I/O Helpers
# ─────────────────────────────────────────────────────────────────────────────

def read_json(filepath: str) -> dict:
    """Read and parse a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data: dict, filepath: str):
    """Write data to a JSON file, creating directories if needed."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_csv(filepath: str) -> list[dict]:
    """Read a CSV file and return list of dictionaries."""
    with open(filepath, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(data: list[dict], filepath: str):
    """Write a list of dicts to a CSV file."""
    if not data:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


# ─────────────────────────────────────────────────────────────────────────────
# Assertion Helpers
# ─────────────────────────────────────────────────────────────────────────────

def assert_response_schema(response_json: dict, required_keys: list):
    """
    Validate that a JSON response contains all required keys.
    Raises AssertionError with a clear message if any key is missing.
    """
    missing = [k for k in required_keys if k not in response_json]
    assert not missing, f"Response schema invalid. Missing keys: {missing}\nGot: {list(response_json.keys())}"


def assert_sorted_ascending(items: list) -> bool:
    """Check if a list is sorted in ascending order."""
    return all(items[i] <= items[i+1] for i in range(len(items)-1))


def assert_sorted_descending(items: list) -> bool:
    return all(items[i] >= items[i+1] for i in range(len(items)-1))


# ─────────────────────────────────────────────────────────────────────────────
# Environment Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_env_var(name: str, default: str = None) -> str:
    """
    Get an environment variable.
    Raises a clear error if required var is missing (no default provided).
    """
    value = os.getenv(name, default)
    if value is None:
        raise EnvironmentError(
            f"Required environment variable '{name}' is not set. "
            f"Please set it in .env or your CI/CD environment."
        )
    return value


def is_ci() -> bool:
    """Returns True if running inside a CI environment (GitHub Actions, Jenkins, etc.)"""
    return os.getenv("CI", "false").lower() == "true"
