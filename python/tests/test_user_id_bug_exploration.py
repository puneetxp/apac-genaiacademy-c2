"""
Bug Condition Exploration Test for User ID BIGINT Consistency

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

This test encodes the EXPECTED BEHAVIOR and will FAIL on unfixed code.
The failure confirms the bug exists. When the fix is implemented, this test will pass.

Property 1: Fault Condition - Schema and Interface Inconsistency Detection
- Test that user.json schema explicitly defines `id` field with BIGINT type
- Test that User.ts interface contains only current schema fields
- Test that all user_id foreign keys consistently use BIGINT type
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pytest


class TestUserIdBugCondition:
    """
    Bug condition exploration tests.

    CRITICAL: These tests MUST FAIL on unfixed code - failure confirms the bug exists.
    DO NOT attempt to fix the test or the code when it fails.
    """

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        # Tests are in cropsense-ai/python/tests/
        # Project root is cropsense-ai/
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def user_schema(self, project_root: Path) -> Dict[str, Any]:
        """Load user.json schema."""
        schema_path = project_root / "database" / "Model" / "user.json"
        with open(schema_path, "r") as f:
            return json.load(f)

    @pytest.fixture
    def user_interface(self, project_root: Path) -> str:
        """Load User.ts TypeScript interface."""
        interface_path = (
            project_root / "solidjs" / "src" / "shared" / "Interface" / "Model" / "User.ts"
        )
        with open(interface_path, "r") as f:
            return f.read()

    @pytest.fixture
    def all_schemas(self, project_root: Path) -> Dict[str, Dict[str, Any]]:
        """Load all model schemas to check foreign key consistency."""
        schemas = {}
        model_dir = project_root / "database" / "Model"
        for schema_file in model_dir.glob("*.json"):
            with open(schema_file, "r") as f:
                schema = json.load(f)
                schemas[schema_file.stem] = schema
        return schemas

    def test_user_schema_has_explicit_id_field(self, user_schema: Dict[str, Any]):
        """
        Test that user.json schema explicitly defines the `id` field.

        Expected Behavior (Requirement 2.1):
        - Schema MUST have an explicit `id` field in the data array
        - Field MUST have datatype "number"
        - Field MUST have mysql_data "bigint" (case-insensitive)
        - Field MUST have PRIMARY KEY in sql_attribute

        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        """
        data_fields = user_schema.get("data", [])
        field_names = [field.get("name") for field in data_fields]

        # Check 1: id field must exist in schema
        assert "id" in field_names, (
            "EXPECTED FAILURE: user.json schema does not explicitly define 'id' field. "
            "This confirms the bug exists - the schema relies on implicit auto-generation."
        )

        # Check 2: Find the id field definition
        id_field = next((field for field in data_fields if field.get("name") == "id"), None)
        assert id_field is not None, "id field not found in schema data array"

        # Check 3: Verify datatype is number
        assert (
            id_field.get("datatype") == "number"
        ), f"id field datatype should be 'number', got '{id_field.get('datatype')}'"

        # Check 4: Verify mysql_data is bigint (case-insensitive)
        mysql_data = id_field.get("mysql_data", "").lower()
        assert (
            mysql_data == "bigint"
        ), f"id field mysql_data should be 'bigint', got '{id_field.get('mysql_data')}'"

        # Check 5: Verify PRIMARY KEY is in sql_attribute
        sql_attribute = id_field.get("sql_attribute", "")
        assert (
            "PRIMARY KEY" in sql_attribute.upper()
        ), f"id field sql_attribute should contain 'PRIMARY KEY', got '{sql_attribute}'"

    def test_user_interface_has_no_deprecated_fields(self, user_interface: str):
        """
        Test that User.ts interface does not contain deprecated authentication fields.

        Expected Behavior (Requirement 2.2):
        - Interface MUST NOT contain google_id field
        - Interface MUST NOT contain facebook_id field
        - Interface MUST NOT contain password field

        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        """
        # Check for deprecated fields
        assert "google_id" not in user_interface, (
            "EXPECTED FAILURE: User.ts interface contains deprecated 'google_id' field. "
            "This field was removed when authentication migrated to AWS Cognito."
        )

        assert "facebook_id" not in user_interface, (
            "EXPECTED FAILURE: User.ts interface contains deprecated 'facebook_id' field. "
            "This field was removed when authentication migrated to AWS Cognito."
        )

        assert "password" not in user_interface, (
            "EXPECTED FAILURE: User.ts interface contains deprecated 'password' field. "
            "This field was removed when authentication migrated to AWS Cognito."
        )

    def test_user_interface_has_current_schema_fields(
        self, user_interface: str, user_schema: Dict[str, Any]
    ):
        """
        Test that User.ts interface contains all current schema fields.

        Expected Behavior (Requirement 2.3):
        - Interface MUST contain cognito_user_id field
        - Interface MUST contain user_type field
        - Interface MUST contain all address-related fields

        EXPECTED OUTCOME: This test FAILS on unfixed code (confirms bug exists)
        """
        # Get all field names from schema
        schema_fields = [field.get("name") for field in user_schema.get("data", [])]

        # Check for key current fields that should be in the interface
        required_fields = [
            "cognito_user_id",
            "user_type",
            "preferred_language",
            "mfa_enabled",
            "latitude",
            "longitude",
            "pincode",
            "state",
            "district",
            "village",
            "address_line",
        ]

        missing_fields = []
        for field in required_fields:
            if field not in user_interface:
                missing_fields.append(field)

        assert len(missing_fields) == 0, (
            f"EXPECTED FAILURE: User.ts interface is missing current schema fields: {missing_fields}. "
            f"The interface is outdated and doesn't reflect the current user.json schema."
        )

    def test_user_id_foreign_keys_use_bigint(self, all_schemas: Dict[str, Dict[str, Any]]):
        """
        Test that all user_id foreign keys consistently use BIGINT type.

        Expected Behavior (Requirement 2.4):
        - All foreign keys referencing users.id MUST use BIGINT type
        - Type should be consistent (case may vary but type must be bigint)

        EXPECTED OUTCOME: This test documents current state and checks for consistency
        """
        foreign_key_types = []

        for schema_name, schema in all_schemas.items():
            if schema_name == "user":
                continue  # Skip the user schema itself

            # Check if this schema has relations to users table
            relations = schema.get("relations", {})
            user_relations = []

            for relation_name, relation_info in relations.items():
                if relation_info.get("table") == "users":
                    field_name = relation_info.get("name")
                    user_relations.append(field_name)

            # For each user relation, check the field type in data array
            data_fields = schema.get("data", [])
            for field in data_fields:
                field_name = field.get("name")
                if (
                    field_name in user_relations
                    or "user_id" in field_name
                    or "farmer_id" in field_name
                    or "buyer_id" in field_name
                ):
                    mysql_data = field.get("mysql_data", "")
                    foreign_key_types.append(
                        {"schema": schema_name, "field": field_name, "type": mysql_data}
                    )

        # Check that all foreign keys use BIGINT (case-insensitive)
        inconsistent_types = []
        for fk in foreign_key_types:
            if fk["type"].lower() != "bigint":
                inconsistent_types.append(fk)

        # Document the findings
        print("\n=== Foreign Key Type Analysis ===")
        print(f"Total user_id foreign keys found: {len(foreign_key_types)}")
        for fk in foreign_key_types:
            print(f"  {fk['schema']}.{fk['field']}: {fk['type']}")

        if inconsistent_types:
            print(f"\nInconsistent types found: {len(inconsistent_types)}")
            for fk in inconsistent_types:
                print(f"  {fk['schema']}.{fk['field']}: {fk['type']} (should be BIGINT)")

        # Assert all use BIGINT
        assert (
            len(inconsistent_types) == 0
        ), f"Found {len(inconsistent_types)} foreign keys not using BIGINT type: {inconsistent_types}"

        # Check for case consistency (document but don't fail)
        case_variations = set(fk["type"] for fk in foreign_key_types)
        if len(case_variations) > 1:
            print(f"\nNote: Multiple case variations found: {case_variations}")
            print("Consider standardizing to lowercase 'bigint' for consistency")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
