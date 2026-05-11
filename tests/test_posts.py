# ─────────────────────────────────────────────
# API Automation Framework - Blog Posts Tests
# ─────────────────────────────────────────────
# API Under Test : JSONPlaceholder
#                  https://jsonplaceholder.typicode.com
# Module         : Blog Posts
# Methods Covered: GET, POST, PUT, PATCH, DELETE
# ─────────────────────────────────────────────

import pytest
import allure
from api.endpoints import PostEndpoints
from utils.schema_validator import schema_validator
from utils.schemas import (
    GET_POSTS_LIST_SCHEMA,
    GET_SINGLE_POST_SCHEMA,
    POST_CREATE_POST_SCHEMA,
    PUT_UPDATE_POST_SCHEMA,
    PATCH_UPDATE_POST_SCHEMA,
)


@allure.epic("Blog Posts Module")
@allure.feature("Posts CRUD")
@pytest.mark.smoke
@pytest.mark.posts
class TestGetPosts:
    """GET /posts and GET /posts/{id}"""

    @allure.story("GET All Posts")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET /posts returns 200 OK")
    def test_get_all_posts_status_code(self, post_client):
        with allure.step("Send GET /posts"):
            response = post_client.get(PostEndpoints.POSTS)
        with allure.step("Assert status 200"):
            assert response.status_code == 200, f"Got {response.status_code}"

    @allure.story("GET All Posts")
    @allure.title("GET /posts returns a non-empty list")
    def test_get_all_posts_returns_list(self, post_client):
        with allure.step("Send GET /posts"):
            response = post_client.get(PostEndpoints.POSTS)
        with allure.step("Assert response is a non-empty list"):
            body = response.json()
            assert isinstance(body, list), "'body' should be a list"
            assert len(body) > 0, "Post list should not be empty"

    @allure.story("GET All Posts")
    @allure.title("GET /posts — schema validation")
    def test_get_all_posts_schema(self, post_client):
        with allure.step("Send GET /posts"):
            response = post_client.get(PostEndpoints.POSTS)
        with allure.step("Validate response schema"):
            schema_validator.validate(response.json(), GET_POSTS_LIST_SCHEMA)

    @allure.story("GET Single Post")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("GET /posts/1 returns 200 and correct id")
    def test_get_single_post_status_and_id(self, post_client):
        with allure.step("Send GET /posts/1"):
            response = post_client.get(PostEndpoints.post_by_id(1))
        with allure.step("Assert status 200"):
            assert response.status_code == 200
        with allure.step("Assert id == 1"):
            assert response.json()["id"] == 1

    @allure.story("GET Single Post")
    @allure.title("GET /posts/1 has all required fields")
    def test_get_single_post_required_fields(self, post_client):
        with allure.step("Send GET /posts/1"):
            response = post_client.get(PostEndpoints.post_by_id(1))
        with allure.step("Assert required fields present"):
            body = response.json()
            for field in ["userId", "id", "title", "body"]:
                assert field in body, f"Field '{field}' missing"

    @allure.story("GET Single Post")
    @allure.title("GET /posts/1 — schema validation")
    def test_get_single_post_schema(self, post_client):
        with allure.step("Send GET /posts/1"):
            response = post_client.get(PostEndpoints.post_by_id(1))
        with allure.step("Validate schema"):
            schema_validator.validate(response.json(), GET_SINGLE_POST_SCHEMA)

    @allure.story("GET Single Post")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("GET /posts/9999 returns 404 Not Found")
    @pytest.mark.negative
    def test_get_nonexistent_post_returns_404(self, post_client):
        with allure.step("Send GET /posts/9999"):
            response = post_client.get(PostEndpoints.post_by_id(9999))
        with allure.step("Assert status 404"):
            assert response.status_code == 404


@allure.epic("Blog Posts Module")
@allure.feature("Posts CRUD")
@pytest.mark.regression
@pytest.mark.posts
class TestCreatePost:
    """POST /posts"""

    @allure.story("POST Create Post")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("POST /posts returns 201 Created")
    def test_create_post_status_code(self, post_client):
        payload = {"userId": 1, "title": "Test Post", "body": "Post body content"}
        with allure.step(f"Send POST /posts with payload: {payload}"):
            response = post_client.post(PostEndpoints.POSTS, payload=payload)
        with allure.step("Assert status 201"):
            assert response.status_code == 201

    @allure.story("POST Create Post")
    @allure.title("POST /posts echoes title and userId")
    def test_create_post_echoes_values(self, post_client):
        payload = {"userId": 1, "title": "Echo Check", "body": "Echo body"}
        with allure.step("Send POST /posts"):
            response = post_client.post(PostEndpoints.POSTS, payload=payload)
        with allure.step("Assert echoed values"):
            body = response.json()
            assert body["title"] == payload["title"]
            assert body["userId"] == payload["userId"]

    @allure.story("POST Create Post")
    @allure.title("POST /posts returns integer id")
    def test_create_post_returns_integer_id(self, post_client):
        payload = {"userId": 1, "title": "ID Test", "body": "Checking id type"}
        with allure.step("Send POST /posts"):
            response = post_client.post(PostEndpoints.POSTS, payload=payload)
        with allure.step("Assert id is integer"):
            assert isinstance(response.json().get("id"), int)

    @allure.story("POST Create Post")
    @allure.title("POST /posts — schema validation")
    def test_create_post_schema(self, post_client):
        payload = {"userId": 1, "title": "Schema Post", "body": "Schema body"}
        with allure.step("Send POST /posts"):
            response = post_client.post(PostEndpoints.POSTS, payload=payload)
        with allure.step("Validate schema"):
            schema_validator.validate(response.json(), POST_CREATE_POST_SCHEMA)


@allure.epic("Blog Posts Module")
@allure.feature("Posts CRUD")
@pytest.mark.regression
@pytest.mark.posts
class TestUpdatePostPut:
    """PUT /posts/{id}"""

    @allure.story("PUT Update Post")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("PUT /posts/1 returns 200")
    def test_put_post_status_code(self, post_client):
        payload = {"userId": 1, "id": 1, "title": "PUT Title", "body": "PUT body"}
        with allure.step("Send PUT /posts/1"):
            response = post_client.put(PostEndpoints.post_by_id(1), payload=payload)
        with allure.step("Assert status 200"):
            assert response.status_code == 200

    @allure.story("PUT Update Post")
    @allure.title("PUT /posts/1 — all fields replaced correctly")
    def test_put_post_all_fields_updated(self, post_client):
        payload = {"userId": 1, "id": 1, "title": "Full Replace Title", "body": "Full Replace Body"}
        with allure.step("Send PUT /posts/1"):
            response = post_client.put(PostEndpoints.post_by_id(1), payload=payload)
        with allure.step("Assert all fields match payload"):
            body = response.json()
            assert body["title"] == payload["title"]
            assert body["body"]  == payload["body"]
            assert body["id"]    == payload["id"]

    @allure.story("PUT Update Post")
    @allure.title("PUT /posts/1 — schema validation")
    def test_put_post_schema(self, post_client):
        payload = {"userId": 1, "id": 1, "title": "Schema PUT", "body": "Body"}
        with allure.step("Send PUT /posts/1"):
            response = post_client.put(PostEndpoints.post_by_id(1), payload=payload)
        with allure.step("Validate schema"):
            schema_validator.validate(response.json(), PUT_UPDATE_POST_SCHEMA)


@allure.epic("Blog Posts Module")
@allure.feature("Posts CRUD")
@pytest.mark.regression
@pytest.mark.posts
class TestUpdatePostPatch:
    """PATCH /posts/{id}"""

    @allure.story("PATCH Update Post")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("PATCH /posts/1 returns 200")
    def test_patch_post_status_code(self, post_client):
        with allure.step("Send PATCH /posts/1 with title only"):
            response = post_client.patch(PostEndpoints.post_by_id(1),
                                         payload={"title": "Patched Title"})
        with allure.step("Assert status 200"):
            assert response.status_code == 200

    @allure.story("PATCH Update Post")
    @allure.title("PATCH /posts/1 — only title updated")
    def test_patch_post_title_only(self, post_client):
        payload = {"title": "Only Title Patched"}
        with allure.step("Send PATCH /posts/1"):
            response = post_client.patch(PostEndpoints.post_by_id(1), payload=payload)
        with allure.step("Assert title reflects patch"):
            assert response.json()["title"] == payload["title"]

    @allure.story("PATCH Update Post")
    @allure.title("PATCH /posts/1 — schema validation")
    def test_patch_post_schema(self, post_client):
        with allure.step("Send PATCH /posts/1"):
            response = post_client.patch(PostEndpoints.post_by_id(1),
                                         payload={"title": "Schema Patch"})
        with allure.step("Validate schema"):
            schema_validator.validate(response.json(), PATCH_UPDATE_POST_SCHEMA)


@allure.epic("Blog Posts Module")
@allure.feature("Posts CRUD")
@pytest.mark.regression
@pytest.mark.posts
class TestDeletePost:
    """DELETE /posts/{id}"""

    @allure.story("DELETE Post")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("DELETE /posts/1 returns 200")
    def test_delete_post_status_code(self, post_client):
        with allure.step("Send DELETE /posts/1"):
            response = post_client.delete(PostEndpoints.post_by_id(1))
        with allure.step("Assert status 200"):
            # JSONPlaceholder returns 200 (not 204) for DELETE
            assert response.status_code == 200

    @allure.story("DELETE Post")
    @allure.title("DELETE /posts/1 returns empty object")
    def test_delete_post_empty_body(self, post_client):
        with allure.step("Send DELETE /posts/1"):
            response = post_client.delete(PostEndpoints.post_by_id(1))
        with allure.step("Assert response is empty object {}"):
            assert response.json() == {}, f"Expected empty dict, got: {response.json()}"

    @allure.story("DELETE Post")
    @allure.title("DELETE multiple posts — all return 200")
    def test_delete_multiple_posts(self, post_client):
        for post_id in [2, 3, 5]:
            with allure.step(f"DELETE /posts/{post_id}"):
                response = post_client.delete(PostEndpoints.post_by_id(post_id))
                assert response.status_code == 200, (
                    f"Expected 200 for post_id={post_id}, got {response.status_code}"
                )