# ─────────────────────────────────────────────
# API Automation Framework - User CRUD Tests
# ─────────────────────────────────────────────
# API Under Test : ReqRes.in  (https://reqres.in/api)
# Module         : User Management
# Methods Covered: GET, POST, PUT, PATCH, DELETE
# ─────────────────────────────────────────────

import pytest
from api.endpoints import UserEndpoints


# ═════════════════════════════════════════════
# GET Tests
# ═════════════════════════════════════════════

@pytest.mark.smoke
@pytest.mark.users
class TestGetUsers:
    """
    Tests for GET /users and GET /users/{id}
    Verifies list fetching, single user fetch,
    pagination, and non-existent user handling.
    """

    def test_get_all_users_status_code(self, user_client):
        """GET /users should return 200 OK."""
        response = user_client.get(UserEndpoints.USERS)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Body: {response.text}"
        )

    def test_get_all_users_returns_list(self, user_client):
        """GET /users response body should contain a 'data' list."""
        response = user_client.get(UserEndpoints.USERS)
        body = response.json()

        assert "data" in body, "'data' key missing from response"
        assert isinstance(body["data"], list), "'data' should be a list"
        assert len(body["data"]) > 0, "User list should not be empty"

    def test_get_all_users_pagination_fields(self, user_client):
        """GET /users response should contain pagination metadata."""
        response = user_client.get(UserEndpoints.USERS)
        body = response.json()

        assert "page" in body, "'page' key missing"
        assert "per_page" in body, "'per_page' key missing"
        assert "total" in body, "'total' key missing"
        assert "total_pages" in body, "'total_pages' key missing"

    def test_get_all_users_page_2(self, user_client):
        """GET /users?page=2 should return page 2 data."""
        response = user_client.get(UserEndpoints.USERS, params={"page": 2})
        body = response.json()

        assert response.status_code == 200
        assert body["page"] == 2, f"Expected page=2, got page={body['page']}"

    def test_get_single_user_status_code(self, user_client):
        """GET /users/2 should return 200 OK."""
        response = user_client.get(UserEndpoints.user_by_id(2))

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )

    def test_get_single_user_correct_id(self, user_client):
        """GET /users/2 should return user with id=2."""
        response = user_client.get(UserEndpoints.user_by_id(2))
        user = response.json()["data"]

        assert user["id"] == 2, f"Expected id=2, got id={user['id']}"

    def test_get_single_user_has_required_fields(self, user_client):
        """GET /users/2 response should have id, email, first_name, last_name."""
        response = user_client.get(UserEndpoints.user_by_id(2))
        user = response.json()["data"]

        required_fields = ["id", "email", "first_name", "last_name", "avatar"]
        for field in required_fields:
            assert field in user, f"Field '{field}' missing from user response"

    def test_get_single_user_email_format(self, user_client):
        """GET /users/2 — email field should contain '@'."""
        response = user_client.get(UserEndpoints.user_by_id(2))
        user = response.json()["data"]

        assert "@" in user["email"], f"Invalid email format: {user['email']}"

    @pytest.mark.negative
    def test_get_nonexistent_user_returns_404(self, user_client):
        """GET /users/9999 should return 404 for a user that doesn't exist."""
        response = user_client.get(UserEndpoints.user_by_id(9999))

        assert response.status_code == 404, (
            f"Expected 404 for non-existent user, got {response.status_code}"
        )

    def test_get_response_content_type_is_json(self, user_client):
        """GET /users should return Content-Type: application/json."""
        response = user_client.get(UserEndpoints.USERS)

        assert "application/json" in response.headers.get("Content-Type", ""), (
            f"Expected JSON Content-Type, got: {response.headers.get('Content-Type')}"
        )


# ═════════════════════════════════════════════
# POST Tests
# ═════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.users
class TestCreateUser:
    """
    Tests for POST /users
    Verifies user creation, response body correctness,
    and status code 201.
    """

    def test_create_user_status_code(self, user_client):
        """POST /users should return 201 Created."""
        payload = {"name": "John Doe", "job": "QA Engineer"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)

        assert response.status_code == 201, (
            f"Expected 201 Created, got {response.status_code}. Body: {response.text}"
        )

    def test_create_user_returns_name(self, user_client):
        """POST /users response should echo back the 'name' we sent."""
        payload = {"name": "Jane Smith", "job": "SDET"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        body = response.json()

        assert body["name"] == "Jane Smith", (
            f"Expected name='Jane Smith', got name='{body.get('name')}'"
        )

    def test_create_user_returns_job(self, user_client):
        """POST /users response should echo back the 'job' we sent."""
        payload = {"name": "Alex Ray", "job": "Automation Lead"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        body = response.json()

        assert body["job"] == "Automation Lead", (
            f"Expected job='Automation Lead', got job='{body.get('job')}'"
        )

    def test_create_user_returns_generated_id(self, user_client):
        """POST /users response should contain a server-generated 'id'."""
        payload = {"name": "Sam Wilson", "job": "DevOps"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        body = response.json()

        assert "id" in body, "'id' field missing from create response"
        assert body["id"] is not None, "'id' should not be None"

    def test_create_user_returns_created_at(self, user_client):
        """POST /users response should include a 'createdAt' timestamp."""
        payload = {"name": "Priya Das", "job": "QA Lead"}
        response = user_client.post(UserEndpoints.USERS, payload=payload)
        body = response.json()

        assert "createdAt" in body, "'createdAt' timestamp missing from response"

    @pytest.mark.negative
    def test_create_user_with_empty_payload(self, user_client):
        """POST /users with empty payload — server still returns 201 (ReqRes behavior)."""
        response = user_client.post(UserEndpoints.USERS, payload={})

        # ReqRes.in returns 201 even for empty body (it's a mock API)
        # In a real app you'd assert 400 Bad Request here
        assert response.status_code == 201, (
            f"Expected 201 from mock API, got {response.status_code}"
        )


# ═════════════════════════════════════════════
# PUT Tests
# ═════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.users
class TestUpdateUserPut:
    """
    Tests for PUT /users/{id}
    PUT = Full update. Replaces the entire resource.
    All fields must be sent in the request.
    """

    def test_put_user_status_code(self, user_client):
        """PUT /users/2 should return 200 OK."""
        payload = {"name": "John Updated", "job": "Senior QA"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Body: {response.text}"
        )

    def test_put_user_name_is_updated(self, user_client):
        """PUT /users/2 — response should reflect the updated name."""
        payload = {"name": "Updated Name", "job": "Lead Engineer"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert body["name"] == "Updated Name", (
            f"Expected name='Updated Name', got '{body.get('name')}'"
        )

    def test_put_user_job_is_updated(self, user_client):
        """PUT /users/2 — response should reflect the updated job."""
        payload = {"name": "Riya Sharma", "job": "Principal QA"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert body["job"] == "Principal QA", (
            f"Expected job='Principal QA', got '{body.get('job')}'"
        )

    def test_put_user_returns_updated_at(self, user_client):
        """PUT /users/2 — response should include an 'updatedAt' timestamp."""
        payload = {"name": "Tom Hardy", "job": "QA Manager"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert "updatedAt" in body, "'updatedAt' timestamp missing from PUT response"

    def test_put_replaces_all_fields(self, user_client):
        """
        PUT sends complete replacement payload.
        Both name and job in response should match exactly what was sent.
        """
        payload = {"name": "Full Replace", "job": "New Role"}
        response = user_client.put(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert body["name"] == payload["name"]
        assert body["job"] == payload["job"]


# ═════════════════════════════════════════════
# PATCH Tests
# ═════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.users
class TestUpdateUserPatch:
    """
    Tests for PATCH /users/{id}
    PATCH = Partial update. Only send the fields you want to change.
    Other fields remain untouched on the server.
    """

    def test_patch_user_status_code(self, user_client):
        """PATCH /users/2 should return 200 OK."""
        payload = {"name": "Partially Updated"}
        response = user_client.patch(UserEndpoints.user_by_id(2), payload=payload)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. Body: {response.text}"
        )

    def test_patch_user_only_name(self, user_client):
        """PATCH /users/2 with only 'name' — response should reflect new name."""
        payload = {"name": "Only Name Changed"}
        response = user_client.patch(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert body["name"] == "Only Name Changed", (
            f"Expected 'Only Name Changed', got '{body.get('name')}'"
        )

    def test_patch_user_only_job(self, user_client):
        """PATCH /users/2 with only 'job' — only job should be updated."""
        payload = {"job": "Patched Job Title"}
        response = user_client.patch(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert body["job"] == "Patched Job Title", (
            f"Expected 'Patched Job Title', got '{body.get('job')}'"
        )

    def test_patch_user_returns_updated_at(self, user_client):
        """PATCH /users/2 — response should include 'updatedAt' timestamp."""
        payload = {"name": "Patch Test"}
        response = user_client.patch(UserEndpoints.user_by_id(2), payload=payload)
        body = response.json()

        assert "updatedAt" in body, "'updatedAt' missing from PATCH response"

    def test_patch_vs_put_difference(self, user_client):
        """
        Demonstrates PUT vs PATCH distinction:
        - PUT  : sends full payload {"name": ..., "job": ...}
        - PATCH: sends partial payload {"job": ...} only
        Both return 200, but PATCH only carries the changed field.
        """
        # PUT — full body
        put_payload = {"name": "Full Body", "job": "Full Role"}
        put_response = user_client.put(UserEndpoints.user_by_id(2), payload=put_payload)
        assert put_response.status_code == 200
        assert put_response.json()["name"] == "Full Body"
        assert put_response.json()["job"] == "Full Role"

        # PATCH — partial body (only job)
        patch_payload = {"job": "Only Job Patched"}
        patch_response = user_client.patch(UserEndpoints.user_by_id(2), payload=patch_payload)
        assert patch_response.status_code == 200
        assert patch_response.json()["job"] == "Only Job Patched"
        # name is NOT in patch response since we didn't send it
        assert "name" not in patch_response.json(), (
            "PATCH response should only contain fields that were sent"
        )


# ═════════════════════════════════════════════
# DELETE Tests
# ═════════════════════════════════════════════

@pytest.mark.regression
@pytest.mark.users
class TestDeleteUser:
    """
    Tests for DELETE /users/{id}
    Verifies correct status code and empty response body.
    """

    def test_delete_user_status_code(self, user_client):
        """DELETE /users/2 should return 204 No Content."""
        response = user_client.delete(UserEndpoints.user_by_id(2))

        assert response.status_code == 204, (
            f"Expected 204 No Content, got {response.status_code}"
        )

    def test_delete_user_empty_response_body(self, user_client):
        """DELETE /users/2 — response body should be empty."""
        response = user_client.delete(UserEndpoints.user_by_id(2))

        assert response.text == "", (
            f"Expected empty body on DELETE, got: '{response.text}'"
        )

    def test_delete_different_user_ids(self, user_client):
        """DELETE should return 204 for any valid user id."""
        for user_id in [1, 3, 5]:
            response = user_client.delete(UserEndpoints.user_by_id(user_id))
            assert response.status_code == 204, (
                f"Expected 204 for user_id={user_id}, got {response.status_code}"
            )

    @pytest.mark.negative
    def test_delete_nonexistent_user(self, user_client):
        """
        DELETE /users/9999 — ReqRes returns 204 even for non-existent IDs.
        In a real app, this might return 404. This test documents the API behavior.
        """
        response = user_client.delete(UserEndpoints.user_by_id(9999))

        # ReqRes is a mock — always returns 204
        # Document what the API actually does here
        assert response.status_code == 204, (
            f"ReqRes mock returns 204 for all DELETEs, got {response.status_code}"
        )