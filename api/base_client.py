# ─────────────────────────────────────────────
# API Automation Framework - Base HTTP Client
# ─────────────────────────────────────────────

import requests
import yaml
import os
import time
from typing import Optional


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


class BaseClient:
    """
    Reusable HTTP client wrapping requests.Session.
    Handles base URL, headers, auth tokens, timeouts,
    x-api-key injection for ReqRes, and 429 auto-retry.
    """

    REQUEST_DELAY    = 0.5    # seconds between every request (avoids rate limit)
    RETRY_ON_429_WAIT = 65    # seconds to wait when 429 is hit

    def __init__(self, service: str = "users"):
        config     = load_config()
        env_name   = config["active_env"]
        env_config = config["environments"][env_name]

        if service == "users":
            self.base_url = env_config["base_url_users"]
        elif service == "posts":
            self.base_url = env_config["base_url_posts"]
        else:
            raise ValueError(f"Unknown service '{service}'. Use 'users' or 'posts'.")

        self.timeout  = env_config["timeout"]
        self.session  = requests.Session()
        self._token: Optional[str] = None

        # ── Default headers ───────────────────
        headers = {
            "Content-Type": "application/json",
            "Accept":       "application/json",
        }

        # ── ReqRes API key (only for reqres.in) ──
        # Injected as x-api-key header on every request.
        # Get your free key at https://reqres.in/signup
        if "reqres.in" in self.base_url:
            api_key = config.get("auth", {}).get("api_key", "")
            if api_key:
                headers["x-api-key"] = api_key
            else:
                print(
                    "\n  ⚠️  WARNING: No ReqRes API key found in config/config.yaml.\n"
                    "     All ReqRes calls will return 401.\n"
                    "     Add your free key at https://reqres.in/signup\n"
                    "     Then set auth.api_key in config/config.yaml\n"
                )

        self.session.headers.update(headers)

    # ─────────────────────────────────────────
    # Auth Token Management
    # ─────────────────────────────────────────

    def set_auth_token(self, token: str):
        """Inject Bearer token for authenticated requests."""
        self._token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def clear_auth_token(self):
        """Remove Bearer token (simulate logout)."""
        self._token = None
        self.session.headers.pop("Authorization", None)

    # ─────────────────────────────────────────
    # Internal dispatcher — delay + 429 retry
    # ─────────────────────────────────────────

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Central request method with:
          • Small delay before every call  → avoids rate limit
          • Auto-retry once on 429         → waits Retry-After header or 65s
        """
        url = f"{self.base_url}{endpoint}"
        time.sleep(self.REQUEST_DELAY)

        response = self.session.request(method, url, timeout=self.timeout, **kwargs)

        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", self.RETRY_ON_429_WAIT))
            print(f"\n  ⏳ 429 Rate Limited — waiting {wait}s before retry...")
            time.sleep(wait)
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)

        return response

    # ─────────────────────────────────────────
    # HTTP Methods
    # ─────────────────────────────────────────

    def get(self, endpoint: str, params: dict = None) -> requests.Response:
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, payload: dict = None) -> requests.Response:
        return self._request("POST", endpoint, json=payload)

    def put(self, endpoint: str, payload: dict = None) -> requests.Response:
        return self._request("PUT", endpoint, json=payload)

    def patch(self, endpoint: str, payload: dict = None) -> requests.Response:
        return self._request("PATCH", endpoint, json=payload)

    def delete(self, endpoint: str) -> requests.Response:
        return self._request("DELETE", endpoint)