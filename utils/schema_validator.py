# ─────────────────────────────────────────────
# API Automation Framework - Schema Validator
# ─────────────────────────────────────────────
# A thin, reusable wrapper around jsonschema
# that produces clean, readable failure messages
# for pytest output.
# ─────────────────────────────────────────────

import json
import jsonschema
from jsonschema import validate, ValidationError, SchemaError
from typing import Union


class SchemaValidator:
    """
    Validates API response bodies against JSON Schema definitions.

    Usage:
        from utils.schema_validator import SchemaValidator
        from utils.schemas import GET_SINGLE_USER_SCHEMA

        validator = SchemaValidator()
        validator.validate(response.json(), GET_SINGLE_USER_SCHEMA)
    """

    def validate(self, response_body: Union[dict, list], schema: dict) -> None:
        """
        Assert that response_body matches the given JSON schema.
        Raises AssertionError with a detailed message on failure —
        so pytest shows exactly what field or type was wrong.

        Args:
            response_body : Parsed JSON (dict or list) from response.json()
            schema        : A JSON Schema dict (from utils/schemas.py)

        Raises:
            AssertionError : With full path + message on validation failure
            AssertionError : If the schema itself is malformed
        """
        try:
            validate(instance=response_body, schema=schema)

        except ValidationError as e:
            # Build a readable path to the failed field
            # e.g.  data → first_name
            field_path = " → ".join(str(p) for p in e.absolute_path) or "root"

            raise AssertionError(
                f"\n{'─'*55}"
                f"\n  ❌ SCHEMA VALIDATION FAILED"
                f"\n{'─'*55}"
                f"\n  Field path : {field_path}"
                f"\n  Problem    : {e.message}"
                f"\n  Validator  : {e.validator} = {e.validator_value}"
                f"\n{'─'*55}"
                f"\n  Full response body:\n"
                f"{json.dumps(response_body, indent=2)}"
                f"\n{'─'*55}"
            ) from e

        except SchemaError as e:
            raise AssertionError(
                f"\n❌ INVALID SCHEMA DEFINITION — fix utils/schemas.py\n"
                f"  Schema error: {e.message}"
            ) from e

    def get_validation_errors(self, response_body: Union[dict, list], schema: dict) -> list:
        """
        Returns a list of all validation errors without raising.
        Useful when you want to collect all failures at once
        rather than stopping at the first one.

        Args:
            response_body : Parsed JSON from response.json()
            schema        : A JSON Schema dict

        Returns:
            list of jsonschema.ValidationError objects (empty if valid)
        """
        validator = jsonschema.Draft7Validator(schema)
        return list(validator.iter_errors(response_body))

    def is_valid(self, response_body: Union[dict, list], schema: dict) -> bool:
        """
        Returns True if response_body is valid against the schema,
        False otherwise. Does NOT raise — useful for conditional logic.

        Args:
            response_body : Parsed JSON from response.json()
            schema        : A JSON Schema dict

        Returns:
            bool
        """
        try:
            validate(instance=response_body, schema=schema)
            return True
        except ValidationError:
            return False


# ─────────────────────────────────────────────
# Module-level singleton — import and use directly
# ─────────────────────────────────────────────
# In your tests, do:
#   from utils.schema_validator import schema_validator
#   schema_validator.validate(response.json(), MY_SCHEMA)
#
schema_validator = SchemaValidator()