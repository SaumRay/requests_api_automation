# ─────────────────────────────────────────────
# API Automation Framework - Allure Labels
# ─────────────────────────────────────────────
# Centralised Allure decorator helpers so every
# test file uses consistent epic/feature/story
# labels — which map directly to the Allure
# report's left-hand navigation tree.
#
# ALLURE HIERARCHY:
#   Epic  → top-level grouping  (e.g. "User Management")
#   Feature → sub-group          (e.g. "User CRUD")
#   Story   → individual scenario (e.g. "GET Single User")
#   Severity → BLOCKER > CRITICAL > NORMAL > MINOR > TRIVIAL
#
# HOW TO USE IN TESTS:
#   from utils.allure_labels import label
#
#   @label.epic_users
#   @label.feature_crud
#   @label.severity_critical
#   class TestGetUsers:
#       @label.story_get_single
#       def test_get_user(self): ...
# ─────────────────────────────────────────────

import allure


class AllureLabels:
    """
    Pre-built Allure decorators for consistent labeling
    across all test classes and methods.
    """

    # ── Epics ─────────────────────────────────
    epic_users = allure.epic("User Management Module")
    epic_auth  = allure.epic("Authentication Module")
    epic_posts = allure.epic("Blog Posts Module")

    # ── Features ──────────────────────────────
    feature_crud      = allure.feature("CRUD Operations")
    feature_auth      = allure.feature("Auth Flow")
    feature_schema    = allure.feature("Schema Validation")
    feature_data      = allure.feature("Data-Driven Testing")

    # ── Stories: User ─────────────────────────
    story_get_all    = allure.story("GET All Records")
    story_get_single = allure.story("GET Single Record")
    story_create     = allure.story("POST Create Record")
    story_put        = allure.story("PUT Full Update")
    story_patch      = allure.story("PATCH Partial Update")
    story_delete     = allure.story("DELETE Record")

    # ── Stories: Auth ─────────────────────────
    story_login      = allure.story("Login Flow")
    story_register   = allure.story("Register Flow")
    story_token      = allure.story("Token Injection")
    story_unauth     = allure.story("Unauthorized Access")

    # ── Severities ────────────────────────────
    severity_blocker  = allure.severity(allure.severity_level.BLOCKER)
    severity_critical = allure.severity(allure.severity_level.CRITICAL)
    severity_normal   = allure.severity(allure.severity_level.NORMAL)
    severity_minor    = allure.severity(allure.severity_level.MINOR)
    severity_trivial  = allure.severity(allure.severity_level.TRIVIAL)


# ─────────────────────────────────────────────
# Module-level singleton — import and decorate
# ─────────────────────────────────────────────
label = AllureLabels()