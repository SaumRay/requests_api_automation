# ─────────────────────────────────────────────
# API Automation Framework - Endpoint Constants
# ─────────────────────────────────────────────
# Centralizing all endpoints here means:
# → No hardcoded URLs scattered across tests
# → One place to update if endpoints change
# ─────────────────────────────────────────────


class UserEndpoints:
    """
    Endpoints for ReqRes.in — User Management & Auth module
    Base URL: https://reqres.in/api
    """

    # ── Auth ──────────────────────────────────
    LOGIN = "/login"
    REGISTER = "/register"

    # ── Users (CRUD) ──────────────────────────
    USERS = "/users"                      # GET all, POST create
    USER_BY_ID = "/users/{id}"           # GET, PUT, PATCH, DELETE by ID

    @staticmethod
    def user_by_id(user_id: int) -> str:
        """Returns the endpoint string for a specific user ID.
        
        Example:
            UserEndpoints.user_by_id(2)  →  '/users/2'
        """
        return f"/users/{user_id}"


class PostEndpoints:
    """
    Endpoints for JSONPlaceholder — Blog Posts module
    Base URL: https://jsonplaceholder.typicode.com
    """

    # ── Posts (CRUD) ──────────────────────────
    POSTS = "/posts"                      # GET all, POST create
    POST_BY_ID = "/posts/{id}"           # GET, PUT, PATCH, DELETE by ID

    # ── Comments (bonus — linked to posts) ────
    COMMENTS = "/comments"
    POST_COMMENTS = "/posts/{id}/comments"

    @staticmethod
    def post_by_id(post_id: int) -> str:
        """Returns the endpoint string for a specific post ID.
        
        Example:
            PostEndpoints.post_by_id(1)  →  '/posts/1'
        """
        return f"/posts/{post_id}"

    @staticmethod
    def comments_for_post(post_id: int) -> str:
        """Returns comments endpoint for a specific post.
        
        Example:
            PostEndpoints.comments_for_post(1)  →  '/posts/1/comments'
        """
        return f"/posts/{post_id}/comments"