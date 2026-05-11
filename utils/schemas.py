# ─────────────────────────────────────────────
# API Automation Framework - JSON Schemas
# ─────────────────────────────────────────────
# NOTE on additionalProperties:
# ReqRes free tier now injects a '_meta' field
# into every response. We remove
# additionalProperties: False from ALL ReqRes
# schemas so _meta is tolerated while still
# validating all required fields and types.
# JSONPlaceholder does NOT inject _meta so we
# keep strict validation there.
# ─────────────────────────────────────────────


# ═════════════════════════════════════════════
# SHARED SUB-SCHEMAS
# ═════════════════════════════════════════════

SINGLE_USER_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "id":         {"type": "integer"},
        "email":      {"type": "string"},
        "first_name": {"type": "string", "minLength": 1},
        "last_name":  {"type": "string", "minLength": 1},
        "avatar":     {"type": "string"}
    },
    "required": ["id", "email", "first_name", "last_name", "avatar"]
    # No additionalProperties: False — ReqRes injects _meta
}

SUPPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "url":  {"type": "string"},
        "text": {"type": "string"}
    },
    "required": ["url", "text"]
}


# ═════════════════════════════════════════════
# USER SCHEMAS  (ReqRes.in)
# additionalProperties NOT set → _meta allowed
# ═════════════════════════════════════════════

GET_USERS_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "page":         {"type": "integer", "minimum": 1},
        "per_page":     {"type": "integer", "minimum": 1},
        "total":        {"type": "integer", "minimum": 0},
        "total_pages":  {"type": "integer", "minimum": 1},
        "data": {
            "type": "array",
            "items": SINGLE_USER_DATA_SCHEMA,
            "minItems": 1
        },
        "support": SUPPORT_SCHEMA
    },
    "required": ["page", "per_page", "total", "total_pages", "data"]
}

GET_SINGLE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "data":    SINGLE_USER_DATA_SCHEMA,
        "support": SUPPORT_SCHEMA
    },
    "required": ["data"]
}

POST_CREATE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "name":      {"type": "string", "minLength": 1},
        "job":       {"type": "string", "minLength": 1},
        "id":        {"type": "string"},
        "createdAt": {"type": "string"}
    },
    "required": ["name", "job", "id", "createdAt"]
}

PUT_UPDATE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "name":      {"type": "string", "minLength": 1},
        "job":       {"type": "string", "minLength": 1},
        "updatedAt": {"type": "string"}
    },
    "required": ["name", "job", "updatedAt"]
}

PATCH_UPDATE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "name":      {"type": "string", "minLength": 1},
        "job":       {"type": "string", "minLength": 1},
        "updatedAt": {"type": "string"}
    },
    "required": ["updatedAt"]
}


# ═════════════════════════════════════════════
# AUTH SCHEMAS  (ReqRes.in)
# additionalProperties NOT set → _meta allowed
# ═════════════════════════════════════════════

LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "token": {"type": "string", "minLength": 1}
    },
    "required": ["token"]
}

LOGIN_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {"type": "string", "minLength": 1}
    },
    "required": ["error"]
}

REGISTER_SUCCESS_SCHEMA = {
    "type": "object",
    "properties": {
        "id":    {"type": "integer"},
        "token": {"type": "string", "minLength": 1}
    },
    "required": ["id", "token"]
}

REGISTER_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {"type": "string", "minLength": 1}
    },
    "required": ["error"]
}


# ═════════════════════════════════════════════
# POST SCHEMAS  (JSONPlaceholder)
# additionalProperties: False SAFE here —
# JSONPlaceholder never injects _meta
# ═════════════════════════════════════════════

GET_POSTS_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "userId": {"type": "integer", "minimum": 1},
            "id":     {"type": "integer", "minimum": 1},
            "title":  {"type": "string",  "minLength": 1},
            "body":   {"type": "string",  "minLength": 1}
        },
        "required": ["userId", "id", "title", "body"],
        "additionalProperties": False
    },
    "minItems": 1
}

GET_SINGLE_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer", "minimum": 1},
        "id":     {"type": "integer", "minimum": 1},
        "title":  {"type": "string",  "minLength": 1},
        "body":   {"type": "string",  "minLength": 1}
    },
    "required": ["userId", "id", "title", "body"],
    "additionalProperties": False
}

POST_CREATE_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer", "minimum": 1},
        "title":  {"type": "string",  "minLength": 1},
        "body":   {"type": "string",  "minLength": 1},
        "id":     {"type": "integer", "minimum": 1}
    },
    "required": ["userId", "title", "body", "id"],
    "additionalProperties": False
}

PUT_UPDATE_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer", "minimum": 1},
        "id":     {"type": "integer", "minimum": 1},
        "title":  {"type": "string",  "minLength": 1},
        "body":   {"type": "string",  "minLength": 1}
    },
    "required": ["userId", "id", "title", "body"],
    "additionalProperties": False
}

PATCH_UPDATE_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer"},
        "id":     {"type": "integer", "minimum": 1},
        "title":  {"type": "string"},
        "body":   {"type": "string"}
    },
    "required": ["id"],
    "additionalProperties": False
}