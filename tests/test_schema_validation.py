# ─────────────────────────────────────────────
# API Automation Framework - Schema Validation Tests
# ─────────────────────────────────────────────
# What this tests:
#   → Every API response body matches its defined schema
#   → All required fields are present
#   → All field data types are correct (int, str, etc.)
#   → No unexpected extra fields slip through
#   → Schema itself correctly REJECTS malformed bodies
#
# APIs  : ReqRes.in (users, auth) + JSONPlaceholder (posts)
# Tool  : jsonschema via utils/schema_validator.py
# ─────────────────────────────────────────────

import pytest
from utils.schema_validator import schema_validator
from utils.schemas import (
    # User schemas
    GET_USERS_LIST_SCHEMA,
    GET_SINGLE_USER_SCHEMA,
    POST_CREATE_USER_SCHEMA,
    PUT_UPDATE_USER_SCHEMA,
    PATCH_UPDATE_USER_SCHEMA,
    # Auth schemas
    LOGIN_SUCCESS_SCHEMA,
    LOGIN_ERROR_SCHEMA,
    REGISTER_SUCCESS_SCHEMA,
    REGISTER_ERROR_SCHEMA,
    # Post schemas
    GET_POSTS_LIST_SCHEMA,
    GET_SINGLE_POST_SCHEMA,
    POST_CREATE_POST_SCHEMA,
    PUT_UPDATE_POST_SCHEMA,
    PATCH_UPDATE_POST_SCHEMA,
)
from api.endpoints import UserEndpoints, PostEndpoints


# ═════════════════════════════════════════════
# USER SCHEMA TESTS  (ReqRes.in)
# ═════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.users
class TestUserSchemas:
    """
    Validates schema contracts for all User Management endpoints.
    These tests catch structural regressions — e.g. a backend
    refactor that renames 'first_name' to 'firstName' would
    cause these tests to fail immediately.
    """

    def test_get_users_list_schema(self, user_client):
        """GET /users — full response must match GET_USERS_LIST_SCHEMA."""
        response = user_client.get(UserEndpoints.USERS)
        assert response.status_code == 200

        # This single call validates: pagination fields, data array,
        # each user object's types, required fields, no extra fields
        schema_validator.validate(response.json(), GET_USERS_LIST_SCHEMA)

    def test_get_users_list_each_user_has_integer_id(self, user_client):
        """GET /users — every user in 'data' must have an integer 'id'."""
        response = user_client.get(UserEndpoints.USERS)
        users = response.json().get("data", [])

        for user in users:
            assert isinstance(user["id"], int), (
                f"Expected integer id, got {type(user['id']).__name__} "
                f"for user: {user}"
            )

    def test_get_users_list_each_user_email_is_string(self, user_client):
        """GET /users — every user's 'email' must be a string."""
        response = user_client.get(UserEndpoints.USERS)
        users = response.json().get("data", [])

        for user in users:
            assert isinstance(user["email"], str), (
                f"Expected string email, got {type(user['email']).__name__}"
            )

    def test_get_single_user_schema(self, user_client):
        """GET /users/2 — response must match GET_SINGLE_USER_SCHEMA."""
        response = user_client.get(UserEndpoints.user_by_id(2))
        assert response.status_code == 200

        schema_validator.validate(response.json(), GET_SINGLE_USER_SCHEMA)

    def test_get_single_user_data_types(self, user_client):
        """GET /users/2 — verify exact types: id=int, names=str, email=str."""
        response = user_client.get(UserEndpoints.user_by_id(2))
        user = response.json()["data"]

        assert isinstance(user["id"],         int), "id must be int"
        assert isinstance(user["email"],      str), "email must be str"
        assert isinstance(user["first_name"], str), "first_name must be str"
        assert isinstance(user["last_name"],  str), "last_name must be str"
        assert isinstance(user["avatar"],     str), "avatar must be str"

    def test_post_create_user_schema(self, user_client):
        """POST /users — creation response must match POST_CREATE_USER_SCHEMA."""
        payload = {"name": "Schema Test User", "job": "QA Engineer"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        assert response.status_code == 201

        schema_validator.validate(response.json(), POST_CREATE_USER_SCHEMA)

    def test_post_create_user_id_is_string(self, user_client):
        """
        POST /users — ReqRes returns 'id' as a STRING (not int).
        This is a known quirk — schema enforces it explicitly.
        In a real app, id would likely be an integer.
        """
        payload = {"name": "Type Check User", "job": "Tester"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        body = response.json()

        assert isinstance(body["id"], str), (
            f"ReqRes POST returns id as string. Got type: {type(body['id']).__name__}"
        )

    def test_post_create_user_created_at_is_string(self, user_client):
        """POST /users — 'createdAt' must be a non-empty string (ISO timestamp)."""
        payload = {"name": "Timestamp User", "job": "Analyst"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        body = response.json()

        assert isinstance(body["createdAt"], str), "'createdAt' must be a string"
        assert len(body["createdAt"]) > 0, "'createdAt' must not be empty"

    def test_put_update_user_schema(self, user_client):
        """PUT /users/2 — update response must match PUT_UPDATE_USER_SCHEMA."""
        payload = {"name": "PUT Schema User", "job": "Senior Engineer"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)
        assert response.status_code == 200

        schema_validator.validate(response.json(), PUT_UPDATE_USER_SCHEMA)

    def test_put_update_user_updated_at_is_string(self, user_client):
        """PUT /users/2 — 'updatedAt' must be a non-empty string timestamp."""
        payload = {"name": "Updated", "job": "Tester"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert isinstance(body["updatedAt"], str), "'updatedAt' must be a string"
        assert len(body["updatedAt"]) > 0, "'updatedAt' must not be empty"

    def test_patch_update_user_schema(self, user_client):
        """PATCH /users/2 — partial update response must match PATCH_UPDATE_USER_SCHEMA."""
        payload = {"name": "Patched Schema User"}
        response = user_client.patch(UserEndpoints.user_by_id(2), payload=payload)
        assert response.status_code == 200

        schema_validator.validate(response.json(), PATCH_UPDATE_USER_SCHEMA)

    def test_patch_only_sends_changed_field(self, user_client):
        """
        PATCH /users/2 with only 'job' — response should only contain
        'job' and 'updatedAt'. 'name' must NOT appear.
        This verifies PATCH does not echo back un-sent fields.
        """
        payload = {"job": "Patched Job Only"}
        response = user_client.patch(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert "job"       in body, "'job' must be in PATCH response"
        assert "updatedAt" in body, "'updatedAt' must be in PATCH response"
        assert "name"     not in body, (
            "'name' was not sent in PATCH — should not appear in response"
        )


# ═════════════════════════════════════════════
# AUTH SCHEMA TESTS  (ReqRes.in)
# ═════════════════════════════════════════════

@pytest.mark.auth
@pytest.mark.regression
class TestAuthSchemas:
    """
    Validates schema contracts for Auth endpoints.
    Ensures login/register success and error responses
    have consistent, predictable structures.
    """

    def test_login_success_schema(self, user_client, config):
        """POST /login success — response must match LOGIN_SUCCESS_SCHEMA."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 200

        schema_validator.validate(response.json(), LOGIN_SUCCESS_SCHEMA)

    def test_login_success_token_is_non_empty_string(self, user_client, config):
        """POST /login — token must be a non-empty string."""
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["valid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        token = response.json().get("token")

        assert isinstance(token, str) and len(token) > 0, (
            f"Token must be a non-empty string. Got: {repr(token)}"
        )

    @pytest.mark.xfail(
        reason=(
            "ReqRes demo API returns 200+token for known emails with wrong password "
            "(_meta.context='legacy_success'). Expected 400 + error schema. "
            "Known read-only demo limitation — not a real auth success. "
            "Track: https://reqres.in — update if API behaviour is restored."
        ),
        strict=True,
    )
    def test_login_error_schema_wrong_password(self, user_client, config):
        """
        POST /login with wrong password — error body must match LOGIN_ERROR_SCHEMA.

        KNOWN ISSUE: ReqRes demo API no longer returns 400 for known registered
        emails with wrong passwords. It returns 200 + token with
        _meta.context='legacy_success'. Marked xfail to document the regression.
        """
        payload = {
            "email":    config["auth"]["valid_email"],
            "password": config["auth"]["invalid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        assert response.status_code == 400, (
            f"Expected 400 for wrong password, got {response.status_code}. Body: {response.text}"
        )
        schema_validator.validate(response.json(), LOGIN_ERROR_SCHEMA)

    def test_login_error_schema_missing_fields(self, user_client):
        """POST /login with empty body — error body must match LOGIN_ERROR_SCHEMA."""
        response = user_client.post(UserEndpoints.LOGIN, payload={})
        assert response.status_code == 400, (
            f"Expected 400 for empty payload, got {response.status_code}. Body: {response.text}"
        )
        schema_validator.validate(response.json(), LOGIN_ERROR_SCHEMA)

    def test_login_error_has_no_token_field(self, user_client, config):
        """
        POST /login failure — token behavior check.
        NOTE: ReqRes free tier returns token even for invalid credentials.
        We document and accept this known free-tier limitation.
        Real API: token must NOT appear in a 400 error response.
        """
        payload = {
            "email":    config["auth"]["invalid_email"],
            "password": config["auth"]["invalid_password"]
        }
        response = user_client.post(UserEndpoints.LOGIN, payload=payload)
        body = response.json()

        assert "token" not in body, (
            f"'token' must not appear in error response. Got: {body}"
        )
        assert "error" in body, f"'error' must appear in error response. Got: {body}"

    def test_register_success_schema(self, user_client):
        """POST /register success — must match REGISTER_SUCCESS_SCHEMA."""
        payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        assert response.status_code == 200

        schema_validator.validate(response.json(), REGISTER_SUCCESS_SCHEMA)

    def test_register_success_id_is_integer(self, user_client):
        """POST /register success — 'id' must be an integer (unlike POST /users)."""
        payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        body = response.json()

        assert isinstance(body["id"], int), (
            f"Register 'id' must be integer. Got: {type(body['id']).__name__}"
        )

    def test_register_error_schema_missing_password(self, user_client):
        """POST /register without password — error body must match REGISTER_ERROR_SCHEMA."""
        payload = {"email": "sydney@fife.com"}
        response = user_client.post(UserEndpoints.REGISTER, payload=payload)
        assert response.status_code == 400

        schema_validator.validate(response.json(), REGISTER_ERROR_SCHEMA)


# ═════════════════════════════════════════════
# POST SCHEMA TESTS  (JSONPlaceholder)
# ═════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.posts
class TestPostSchemas:
    """
    Validates schema contracts for the Blog Posts module.
    JSONPlaceholder is consistent — these schemas act as
    a regression guard for the posts API shape.
    """

    def test_get_posts_list_schema(self, post_client):
        """GET /posts — full array must match GET_POSTS_LIST_SCHEMA."""
        response = post_client.get(PostEndpoints.POSTS)
        assert response.status_code == 200

        schema_validator.validate(response.json(), GET_POSTS_LIST_SCHEMA)

    def test_get_posts_list_all_items_have_required_fields(self, post_client):
        """GET /posts — every post must have userId, id, title, body."""
        response = post_client.get(PostEndpoints.POSTS)
        posts = response.json()

        required = ["userId", "id", "title", "body"]
        for post in posts:
            for field in required:
                assert field in post, (
                    f"Field '{field}' missing from post: {post}"
                )

    def test_get_posts_list_types(self, post_client):
        """GET /posts — verify integer ids and string titles/bodies."""
        response = post_client.get(PostEndpoints.POSTS)
        posts = response.json()

        for post in posts[:5]:  # spot check first 5
            assert isinstance(post["userId"], int), "userId must be int"
            assert isinstance(post["id"],     int), "id must be int"
            assert isinstance(post["title"],  str), "title must be str"
            assert isinstance(post["body"],   str), "body must be str"

    def test_get_single_post_schema(self, post_client):
        """GET /posts/1 — response must match GET_SINGLE_POST_SCHEMA."""
        response = post_client.get(PostEndpoints.post_by_id(1))
        assert response.status_code == 200

        schema_validator.validate(response.json(), GET_SINGLE_POST_SCHEMA)

    def test_get_single_post_id_matches_requested(self, post_client):
        """GET /posts/1 — response 'id' must equal the requested ID."""
        response = post_client.get(PostEndpoints.post_by_id(1))
        body = response.json()

        assert body["id"] == 1, f"Expected id=1, got id={body['id']}"

    def test_post_create_post_schema(self, post_client):
        """POST /posts — creation response must match POST_CREATE_POST_SCHEMA."""
        payload = {
            "userId": 1,
            "title":  "Schema Validation Post",
            "body":   "Testing schema contract for create response"
        }
        response = post_client.post(PostEndpoints.POSTS, payload=payload)
        assert response.status_code == 201

        schema_validator.validate(response.json(), POST_CREATE_POST_SCHEMA)

    def test_post_create_post_returns_integer_id(self, post_client):
        """POST /posts — newly created post 'id' must be an integer."""
        payload = {"userId": 1, "title": "ID Type Check", "body": "Checking type"}
        response = post_client.post(PostEndpoints.POSTS, payload=payload)
        body = response.json()

        assert isinstance(body["id"], int), (
            f"Expected integer id from POST /posts, got: {type(body['id']).__name__}"
        )

    def test_put_update_post_schema(self, post_client):
        """PUT /posts/1 — full update response must match PUT_UPDATE_POST_SCHEMA."""
        payload = {
            "userId": 1,
            "id":     1,
            "title":  "PUT Schema Test Title",
            "body":   "PUT body content for schema check"
        }
        response = post_client.put(PostEndpoints.post_by_id(1), payload=payload)
        assert response.status_code == 200

        schema_validator.validate(response.json(), PUT_UPDATE_POST_SCHEMA)

    def test_patch_update_post_schema(self, post_client):
        """PATCH /posts/1 — partial update response must match PATCH_UPDATE_POST_SCHEMA."""
        payload = {"title": "PATCH Schema Updated Title"}
        response = post_client.patch(PostEndpoints.post_by_id(1), payload=payload)
        assert response.status_code == 200

        schema_validator.validate(response.json(), PATCH_UPDATE_POST_SCHEMA)


# ═════════════════════════════════════════════
# SCHEMA VALIDATOR UNIT TESTS
# ═════════════════════════════════════════════

@pytest.mark.regression
class TestSchemaValidatorBehavior:
    """
    Tests for the SchemaValidator utility itself.
    Verifies it correctly PASSES valid data and
    correctly REJECTS invalid data with helpful messages.
    These are pure unit tests — no HTTP calls made.
    """

    def test_validator_passes_valid_data(self):
        """schema_validator.validate() must NOT raise for a valid payload."""
        valid_body = {
            "token": "QpwL5tpe83ilfN2"
        }
        # Should not raise anything
        schema_validator.validate(valid_body, LOGIN_SUCCESS_SCHEMA)

    def test_validator_raises_on_missing_required_field(self):
        """schema_validator.validate() must raise AssertionError if required field is absent."""
        body_missing_token = {}   # 'token' is required but missing

        with pytest.raises(AssertionError) as exc_info:
            schema_validator.validate(body_missing_token, LOGIN_SUCCESS_SCHEMA)

        assert "SCHEMA VALIDATION FAILED" in str(exc_info.value)

    def test_validator_raises_on_wrong_type(self):
        """schema_validator.validate() must raise if a field has the wrong type."""
        wrong_type_body = {
            "id":         "not-an-int",   # should be integer
            "email":      "test@example.com",
            "first_name": "Test",
            "last_name":  "User",
            "avatar":     "https://example.com/avatar.jpg"
        }
        with pytest.raises(AssertionError) as exc_info:
            schema_validator.validate(
                {"data": wrong_type_body},
                GET_SINGLE_USER_SCHEMA
            )
        assert "SCHEMA VALIDATION FAILED" in str(exc_info.value)

    def test_validator_raises_on_extra_unexpected_field(self):
        """
        schema_validator.validate() must raise if an unexpected field appears
        in a schema that uses additionalProperties: False.
        JSONPlaceholder post schemas use strict mode — we use GET_SINGLE_POST_SCHEMA.
        """
        body_with_extra = {
            "userId": 1,
            "id":     1,
            "title":  "Test Title",
            "body":   "Test Body",
            "extra_field": "not allowed"  # not in schema
        }
        with pytest.raises(AssertionError) as exc_info:
            schema_validator.validate(body_with_extra, GET_SINGLE_POST_SCHEMA)

        assert "SCHEMA VALIDATION FAILED" in str(exc_info.value)

    def test_is_valid_returns_true_for_valid_data(self):
        """schema_validator.is_valid() must return True for correct data."""
        valid = {"token": "abc123xyz"}
        assert schema_validator.is_valid(valid, LOGIN_SUCCESS_SCHEMA) is True

    def test_is_valid_returns_false_for_invalid_data(self):
        """schema_validator.is_valid() must return False for invalid data."""
        invalid = {"not_token": "abc123"}
        assert schema_validator.is_valid(invalid, LOGIN_SUCCESS_SCHEMA) is False

    def test_get_validation_errors_returns_empty_list_for_valid(self):
        """schema_validator.get_validation_errors() returns [] for valid data."""
        valid = {"token": "abc123xyz"}
        errors = schema_validator.get_validation_errors(valid, LOGIN_SUCCESS_SCHEMA)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_get_validation_errors_returns_list_for_invalid(self):
        """schema_validator.get_validation_errors() returns error list for invalid data."""
        invalid = {}   # missing required 'token'
        errors = schema_validator.get_validation_errors(invalid, LOGIN_SUCCESS_SCHEMA)
        assert len(errors) > 0, "Expected at least one validation error"

    def test_error_message_includes_field_path(self):
        """
        AssertionError message from validate() must mention the failing field path.
        This is critical for debugging failures in CI pipelines.
        """
        bad_body = {"token": 12345}   # token should be string, not int
        with pytest.raises(AssertionError) as exc_info:
            schema_validator.validate(bad_body, LOGIN_SUCCESS_SCHEMA)

        error_text = str(exc_info.value)
        assert "token" in error_text, (
            f"Error message should mention the failing field 'token'. Got:\n{error_text}"
        )