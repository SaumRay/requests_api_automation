# ─────────────────────────────────────────────
# API Automation Framework - conftest.py
# ─────────────────────────────────────────────
# pytest automatically picks up this file.
# Fixtures defined here are available to ALL
# test files without any imports needed.
# ─────────────────────────────────────────────

import pytest
import yaml
import os
import allure
from api.base_client import BaseClient


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# ─────────────────────────────────────────────
# Scope: "session" → created ONCE per test run
# ─────────────────────────────────────────────

@pytest.fixture(scope="session")
def config():
    """Loads and returns config.yaml as a dict."""
    return load_config()


@pytest.fixture(scope="session")
def user_client():
    """BaseClient for User Management API (ReqRes.in)."""
    return BaseClient(service="users")


@pytest.fixture(scope="session")
def post_client():
    """BaseClient for Blog Posts API (JSONPlaceholder)."""
    return BaseClient(service="posts")


@pytest.fixture(scope="session")
def auth_token(user_client, config):
    """Logs in once per session, returns the Bearer token."""
    credentials = {
        "email": config["auth"]["valid_email"],
        "password": config["auth"]["valid_password"]
    }
    response = user_client.post("/login", payload=credentials)
    assert response.status_code == 200, f"Login failed during setup: {response.text}"
    token = response.json().get("token")
    assert token, "No token returned from login"
    return token


@pytest.fixture(scope="function")
def authenticated_user_client(user_client, auth_token):
    """User client with Bearer token pre-set. Cleared after each test."""
    user_client.set_auth_token(auth_token)
    yield user_client
    user_client.clear_auth_token()


# ─────────────────────────────────────────────
# Allure: attach request/response on failure
# ─────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    After each test, if it FAILED, attach the last
    request/response details to the Allure report.
    This gives you full context without digging through logs.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Attach the failure longrepr as an Allure text attachment
        allure.attach(
            str(report.longreprtext) if hasattr(report, "longreprtext") else str(report.longrepr),
            name="Failure Details",
            attachment_type=allure.attachment_type.TEXT
        )


# ─────────────────────────────────────────────
# HTML Report: enrich with environment metadata
# ─────────────────────────────────────────────

def pytest_configure(config):
    """
    Add environment metadata to the HTML report header.
    Shown at the top of reports/test_report.html.
    """
    config._metadata = getattr(config, "_metadata", {})
    config._metadata.update({
        "Project"     : "API Automation Framework",
        "Author"      : "QA Engineer",
        "Base URL (Users)": "https://reqres.in/api",
        "Base URL (Posts)": "https://jsonplaceholder.typicode.com",
        "Framework"   : "Python + Requests + pytest",
        "Reporting"   : "pytest-html + Allure",
    })


def pytest_html_report_title(report):
    """Set a custom title for the HTML report."""
    report.title = "API Automation Test Report — User Management & Blog Posts"