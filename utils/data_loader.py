# ─────────────────────────────────────────────
# API Automation Framework - Data Loader
# ─────────────────────────────────────────────
# Reads test data from JSON files in test_data/
# and converts them into formats that pytest's
# @pytest.mark.parametrize can directly consume.
#
# WHY A DATA LOADER?
# → Keeps test data OUT of test files
# → Non-engineers (BAs, PMs) can add test cases
#   by editing JSON — no Python needed
# → Makes it easy to scale: 3 cases → 300 cases
#   without touching test code
# ─────────────────────────────────────────────

import json
import os
from typing import Any


# Base path for all test data files
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "test_data")


def load_json(filename: str) -> dict:
    """
    Load and return a JSON test data file as a dict.

    Args:
        filename (str): File name inside test_data/ e.g. 'users.json'

    Returns:
        dict: Parsed JSON content

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is malformed JSON
    """
    filepath = os.path.join(TEST_DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Test data file not found: {filepath}\n"
            f"Make sure '{filename}' exists in the test_data/ directory."
        )

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_parametrize_data(filename: str, key: str) -> list[tuple]:
    """
    Load a specific list from a JSON file and convert it to
    a list of tuples for use with @pytest.mark.parametrize.

    Each item in the JSON list becomes one test case.

    Args:
        filename (str) : JSON file name e.g. 'users.json'
        key      (str) : Top-level key in the JSON e.g. 'create_users'

    Returns:
        list of tuples: Each tuple is (test_case_id, test_case_dict)

    Example:
        @pytest.mark.parametrize("tc_id, data",
            data_loader.get_parametrize_data("users.json", "create_users"))
        def test_create_user(tc_id, data, user_client):
            ...
    """
    raw = load_json(filename)

    if key not in raw:
        raise KeyError(
            f"Key '{key}' not found in '{filename}'.\n"
            f"Available keys: {list(raw.keys())}"
        )

    items = raw[key]

    if not isinstance(items, list):
        raise TypeError(
            f"Expected a list under key '{key}', got {type(items).__name__}"
        )

    # Return as (id, full_dict) tuples so pytest labels each test
    # with the test case ID e.g. TC_USR_CREATE_001
    return [(item["id"], item) for item in items]


def get_ids(filename: str, key: str) -> list[str]:
    """
    Returns just the test case IDs for a given key.
    Useful for the `ids` parameter of @pytest.mark.parametrize
    when you want cleaner test output labels.

    Args:
        filename (str): JSON file name
        key      (str): Top-level key

    Returns:
        list of strings: e.g. ['TC_USR_CREATE_001', 'TC_USR_CREATE_002']
    """
    raw = load_json(filename)
    return [item["id"] for item in raw.get(key, [])]


def get_raw_list(filename: str, key: str) -> list[dict]:
    """
    Returns the raw list of test case dicts for a given key.
    Use this when you want to iterate manually in a test.

    Args:
        filename (str): JSON file name
        key      (str): Top-level key

    Returns:
        list of dicts
    """
    raw = load_json(filename)
    return raw.get(key, [])


# ─────────────────────────────────────────────
# Module-level singleton — import and use directly
# ─────────────────────────────────────────────
# In your tests:
#   from utils.data_loader import data_loader
#   data_loader.get_parametrize_data("users.json", "create_users")
#
class DataLoader:
    """Wrapper class for convenient import and use."""

    def load_json(self, filename: str) -> dict:
        return load_json(filename)

    def get_parametrize_data(self, filename: str, key: str) -> list[tuple]:
        return get_parametrize_data(filename, key)

    def get_ids(self, filename: str, key: str) -> list[str]:
        return get_ids(filename, key)

    def get_raw_list(self, filename: str, key: str) -> list[dict]:
        return get_raw_list(filename, key)


data_loader = DataLoader()