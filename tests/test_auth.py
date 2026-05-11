# ─────────────────────────────────────────────
# API Automation Framework - Auth Tests
# ─────────────────────────────────────────────
# API Under Test : ReqRes.in  (https://reqres.in/api)
# Module         : Authentication
# Covers         :
#   → POST /login  (valid, invalid, missing fields)
#   → POST /register (success, missing password)
#   → Token extraction & structure validation
#   → Bearer token injection into protected requests
#   → Unauthorized access (no token / wrong token)
# ─────────────────────────────────────────────

import pytest
from api.endpoints import UserEndpoints


# ═════════════════════════════════════════════
# LOGIN Tests — POST /login
# ═════════════════════════════════════════════

@pytest.mark.auth
@pytest.mark.smoke
class TestLogin:
    """Tests for POST /login"""

    def test_valid_login_status_code(self, user_client, config):
        """POST /login with valid credentials should return 200 OK."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 200, (
            f"Expected 200 for valid login, got {response.status_code}. Body: {response.text}"
        )

    def test_valid_login_returns_token(self, user_client, config):
        """POST /login — response must contain a 'token'."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        body = response.json()
        assert "token" in body, f"'token' key missing from login response. Got: {body}"
        assert body["token"] not in [None, ""], "'token' should not be None or empty"

    def test_valid_login_token_is_string(self, user_client, config):
        """POST /login — the returned token must be a string."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        token = response.json().get("token")
        assert isinstance(token, str), f"Expected string token, got {type(token).__name__}"

    def test_valid_login_token_min_length(self, user_client, config):
        """POST /login — token length should be > 5 chars."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        token = response.json().get("token", "")
        assert len(token) > 5, f"Token too short: '{token}' (len={len(token)})"

    def test_valid_login_response_content_type(self, user_client, config):
        """POST /login — response Content-Type should be application/json."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert "application/json" in response.headers.get("Content-Type", ""), (
            f"Expected JSON content type, got: {response.headers.get('Content-Type')}"
        )

    @pytest.mark.negative
    @pytest.mark.xfail(
        reason=(
            "ReqRes demo API changed behaviour: POST /login with a known email "
            "and wrong password now returns 200 + token instead of 400. "
            "The _meta.context field is 'legacy_success', confirming this is a "
            "read-only demo limitation — not a real auth success. "
            "Track: https://reqres.in — update if API behaviour is restored."
        ),
        strict=True,
    )
    def test_invalid_password_returns_400(self, user_client, config):
        """
        POST /login with wrong password → expected 400.

        KNOWN ISSUE: ReqRes demo API no longer validates passwords for known
        registered emails (e.g. eve.holt@reqres.in). It returns 200 + token
        with _meta.context='legacy_success' regardless of the password supplied.
        This test is marked xfail to document the regression without hiding it.
        A real production API must return 400/401 for wrong credentials.
        """
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["invalid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 400, (
            f"Expected 400 for invalid password, got {response.status_code}. Body: {response.text}"
        )

    @pytest.mark.negative
    def test_invalid_login_returns_error_message(self, user_client, config):
        """POST /login with wrong credentials — response body should contain 'error'."""
        payload = {
            "email":    config["auth"]["invalid_email"],
            "password": config["auth"]["invalid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        body = response.json()
        assert "error" in body, f"Expected 'error' key in response. Got: {body}"

    @pytest.mark.negative
    def test_invalid_login_no_token_in_error_response(self, user_client, config):
        """POST /login failure — 'token' must NOT appear in the error response."""
        payload = {
            "email":    config["auth"]["invalid_email"],
            "password": config["auth"]["invalid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        body = response.json()
        assert "token" not in body, (
            f"'token' should NOT appear in a failed login response. Got: {body}"
        )

    @pytest.mark.negative
    def test_login_missing_password_returns_400(self, user_client, config):
        """POST /login with only email — should return 400."""
        payload = {"email": config["auth"]["valid_email"]}
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 400, (
            f"Expected 400 when password is missing, got {response.status_code}"
        )

    @pytest.mark.negative
    def test_login_missing_email_returns_400(self, user_client, config):
        """POST /login with only password — should return 400."""
        payload = {"password": config["auth"]["valid_password"]}
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 400, (
            f"Expected 400 when email is missing, got {response.status_code}"
        )

    @pytest.mark.negative
    def test_login_empty_payload_returns_400(self, user_client):
        """POST /login with empty body — should return 400."""
        response = user_client.post(UserEndpoints.LOGIN, payload={})
        assert response.status_code == 400, (
            f"Expected 400 for empty login payload, got {response.status_code}"
        )


# ═════════════════════════════════════════════
# REGISTER Tests — POST /register
# ═════════════════════════════════════════════

@pytest.mark.auth
@pytest.mark.regression
class TestRegister:
    """Tests for POST /register"""

    def test_valid_register_status_code(self, user_client):
        """POST /register with valid credentials should return 200."""
        payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        assert response.status_code == 200, (
            f"Expected 200 for valid register, got {response.status_code}. Body: {response.text}"
        )

    def test_valid_register_returns_id(self, user_client):
        """POST /register — response must contain a user 'id'."""
        payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        body = response.json()
        assert "id" in body, f"'id' missing from register response. Got: {body}"
        assert body["id"] is not None

    def test_valid_register_returns_token(self, user_client):
        """POST /register — response must contain a 'token'."""
        payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        body = response.json()
        assert "token" in body, f"'token' missing from register response. Got: {body}"
        assert body["token"] != ""

    @pytest.mark.negative
    def test_register_missing_password_returns_400(self, user_client):
        """POST /register without password should return 400."""
        payload = {"email": "sydney@fife.com"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        assert response.status_code == 400, (
            f"Expected 400 for missing password, got {response.status_code}"
        )

    @pytest.mark.negative
    def test_register_missing_password_error_message(self, user_client):
        """POST /register without password — response should have an 'error' message."""
        payload = {"email": "sydney@fife.com"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        body = response.json()
        assert "error" in body, f"Expected 'error' in body. Got: {body}"
        assert body["error"] != ""


# ═════════════════════════════════════════════
# TOKEN INJECTION Tests
# ═════════════════════════════════════════════

@pytest.mark.auth
@pytest.mark.regression
class TestTokenInjection:
    """Tests for Bearer token extraction and header injection."""

    def test_auth_token_fixture_is_available(self, auth_token):
        """auth_token fixture should return a non-empty string token."""
        assert auth_token is not None
        assert isinstance(auth_token, str)
        assert len(auth_token) > 0

    def test_set_auth_token_updates_headers(self, user_client, auth_token):
        """set_auth_token() should inject 'Bearer <token>' into headers."""
        user_client.set_auth_token(auth_token)
        auth_header = user_client.session.headers.get("Authorization", "")
        assert auth_header.startswith("Bearer "), f"Expected 'Bearer <token>', got: '{auth_header}'"
        assert auth_token in auth_header
        user_client.clear_auth_token()

    def test_clear_auth_token_removes_header(self, user_client, auth_token):
        """clear_auth_token() should remove the Authorization header."""
        user_client.set_auth_token(auth_token)
        user_client.clear_auth_token()
        assert user_client.session.headers.get("Authorization") is None

    def test_authenticated_client_fixture_has_token(self, authenticated_user_client, auth_token):
        """authenticated_user_client fixture should pre-set Bearer token."""
        auth_header = authenticated_user_client.session.headers.get("Authorization", "")
        assert "Bearer" in auth_header

    def test_authenticated_client_can_make_get_request(self, authenticated_user_client):
        """Authenticated GET /users/2 should return 200."""
        response = authenticated_user_client.get(UserEndpoints.user_by_id(2))
        assert response.status_code == 200, (
            f"Authenticated GET failed. Status: {response.status_code}, Body: {response.text}"
        )

    def test_token_consistent_across_multiple_calls(self, user_client, config):
        """Same credentials should return same token on each login."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        token_1 = user_client.post(UserEndpoints.LOGIN, payload=payload).json().get("token")
        token_2 = user_client.post(UserEndpoints.LOGIN, payload=payload).json().get("token")
        assert token_1 == token_2, f"Tokens differ: '{token_1}' vs '{token_2}'"


# ═════════════════════════════════════════════
# UNAUTHORIZED ACCESS Tests
# ═════════════════════════════════════════════

@pytest.mark.auth
@pytest.mark.negative
class TestUnauthorizedAccess:
    """Tests for missing/invalid auth token behavior."""

    def test_request_without_token_still_returns_200_on_mock(self, user_client):
        """
        GET /users/2 without Authorization header.
        With a valid x-api-key but no Bearer token, ReqRes still returns 200
        for GET endpoints (Bearer is only needed for per-user sessions).
        """
        user_client.clear_auth_token()
        response = user_client.get(UserEndpoints.user_by_id(2))
        assert response.status_code == 200, (
            f"Expected 200 for GET without Bearer token. Got: {response.status_code}. "
            f"Body: {response.text}"
        )

    def test_request_with_invalid_token_behavior(self, user_client):
        """GET /users/2 with a fake Bearer token — ReqRes accepts it for GET."""
        user_client.set_auth_token("invalid_fake_token_xyz_000")
        response = user_client.get(UserEndpoints.user_by_id(2))
        assert response.status_code in [200, 401], (
            f"Unexpected status with invalid token: {response.status_code}"
        )
        user_client.clear_auth_token()

    def test_login_with_unregistered_user_returns_400(self, user_client):
        """POST /login with unknown email → 400."""
        payload = {"email": "ghost_user_xyz@notexist.com", "password": "nopassword"}
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 400, (
            f"Expected 400 for unregistered user, got {response.status_code}"
        )

    def test_login_error_body_has_error_field(self, user_client):
        """POST /login failure — response body must contain 'error' field."""
        payload = {"email": "ghost_user_xyz@notexist.com", "password": "nopassword"}
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        body = response.json()
        assert "error" in body, f"Expected 'error' key in 400 body. Got: {body}"
        assert len(body["error"]) > 0