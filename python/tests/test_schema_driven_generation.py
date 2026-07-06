"""
Test AC0: Schema-Driven Code Generation System
Validates that JSON schemas generate complete FastAPI backend, SolidJS frontend, 
and PostgreSQL migrations with role-based CRUD permissions
"""

import pytest
import os
import json
from pathlib import Path


class TestSchemaCodeGeneration:
    """Test suite for schema-driven code generation validation"""
    
    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def schema_dir(self, project_root):
        """Get schema directory"""
        return project_root / "database" / "Model"
    
    def test_json_schemas_exist(self, schema_dir):
        """
        AC0: Verify JSON schemas exist in database/Model/ directory
        
        Requirements:
        - At least 13 JSON schema files should exist
        - Each schema should be valid JSON
        - Schemas should define data models for the platform
        """
        assert schema_dir.exists(), f"Schema directory not found: {schema_dir}"
        
        # Get all JSON files
        json_files = list(schema_dir.glob("*.json"))
        
        # Should have at least 13 schemas (as per requirements)
        assert len(json_files) >= 13, f"Expected at least 13 schemas, found {len(json_files)}"
        
        # Verify each is valid JSON
        for json_file in json_files:
            with open(json_file, 'r') as f:
                try:
                    data = json.load(f)
                    assert isinstance(data, dict), f"{json_file.name} should contain a JSON object"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {json_file.name}: {e}")
    
    def test_schema_structure(self, schema_dir):
        """
        AC0: Verify schemas have required structure
        
        Requirements:
        - Each schema should have: name, table, crud, enable, data fields
        - CRUD permissions should be configured (isuper, islogin)
        - Data fields should define model structure
        """
        json_files = list(schema_dir.glob("*.json"))
        
        for json_file in json_files:
            with open(json_file, 'r') as f:
                schema = json.load(f)
                
                # Check required top-level fields
                assert "name" in schema, f"{json_file.name} missing 'name' field"
                assert "table" in schema, f"{json_file.name} missing 'table' field"
                assert "crud" in schema, f"{json_file.name} missing 'crud' field"
                assert "enable" in schema, f"{json_file.name} missing 'enable' field"
                assert "data" in schema, f"{json_file.name} missing 'data' field"
                
                # Verify CRUD permissions structure
                crud = schema["crud"]
                assert isinstance(crud, dict), f"{json_file.name} crud should be a dict"
                # Should have at least one role defined
                assert len(crud) > 0, f"{json_file.name} should have CRUD permissions defined"
                
                # Verify data fields
                data = schema["data"]
                assert isinstance(data, list), f"{json_file.name} data should be a list"
    
    def test_fastapi_backend_generated(self, project_root):
        """
        AC0: Verify FastAPI backend code is generated
        
        Requirements:
        - Models should exist in python/app/orm/
        - Schemas should exist in python/app/schemas/
        - Services should exist in python/app/services/
        - API routers should exist in python/app/
        """
        backend_dir = project_root / "python" / "app"
        
        # Check directory structure
        assert (backend_dir / "orm").exists(), "ORM models directory not found"
        assert (backend_dir / "schemas").exists(), "Schemas directory not found"
        assert (backend_dir / "services").exists(), "Services directory not found"
        assert (backend_dir / "api" / "v1").exists(), "API routers directory not found"
        
        # Check for generated model files
        orm_files = list((backend_dir / "orm").glob("*.py"))
        assert len(orm_files) > 0, "No ORM model files generated"
        
        # Check for generated schema files
        schema_files = list((backend_dir / "schemas").glob("*.py"))
        assert len(schema_files) > 0, "No schema files generated"
        
        # Check for generated service files
        service_files = list((backend_dir / "services").glob("*.py"))
        assert len(service_files) > 0, "No service files generated"
        
        # Check for generated router files
        router_files = list((backend_dir / "api" / "v1").glob("*.py"))
        assert len(router_files) > 0, "No router files generated"
    
    def test_solidjs_frontend_generated(self, project_root):
        """
        AC0: Verify SolidJS frontend code is generated
        
        Requirements:
        - TypeScript interfaces should exist in solidjs/src/shared/Interface/Model/
        - API services should exist in solidjs/src/shared/Service/
        - Stores should exist in solidjs/src/stores/ (custom location)
        """
        frontend_dir = project_root / "solidjs" / "src"
        
        # Check directory structure
        assert (frontend_dir / "shared" / "Interface" / "Model").exists(), \
            "TypeScript interfaces directory not found"
        assert (frontend_dir / "shared" / "Service").exists(), \
            "API services directory not found"
        assert (frontend_dir / "stores").exists(), \
            "Stores directory not found"
        
        # Check for generated interface files
        interface_files = list((frontend_dir / "shared" / "Interface" / "Model").glob("*.ts"))
        assert len(interface_files) > 0, "No TypeScript interface files generated"
        
        # Check for generated service files
        service_files = list((frontend_dir / "shared" / "Service").glob("*.ts"))
        assert len(service_files) > 0, "No API service files generated"
        
        # Check for store files (custom stores in src/stores/)
        store_files = list((frontend_dir / "stores").glob("*.ts"))
        assert len(store_files) > 0, "No store files generated"
    
    def test_custom_services_preserved(self, project_root):
        """
        AC0: Verify custom business logic services are preserved
        
        Requirements:
        - bedrock_service.py should exist (custom AI integration)
        - marketplace_service.py should exist (custom marketplace logic)
        - weather_service.py should exist (custom weather integration)
        """
        services_dir = project_root / "python" / "app" / "services"
        
        # Check custom service files
        assert (services_dir / "bedrock_service.py").exists(), \
            "bedrock_service.py not found - custom AI service missing"
        assert (services_dir / "marketplace_service.py").exists(), \
            "marketplace_service.py not found - custom marketplace service missing"
        assert (services_dir / "weather_service.py").exists(), \
            "weather_service.py not found - custom weather service missing"
    
    def test_code_generation_config(self, project_root):
        """
        AC0: Verify code generation configuration
        
        Requirements:
        - config.json should exist with proper settings
        - setup.php should exist for code generation
        - Configuration should specify FastAPI and SolidJS
        """
        # Check config.json
        config_file = project_root / "config.json"
        assert config_file.exists(), "config.json not found"
        
        with open(config_file, 'r') as f:
            config = json.load(f)
            
            # Verify backend configuration
            assert "back-end" in config, "Backend configuration missing"
            assert "python" in config["back-end"], "Python backend not configured"
            
            # Verify frontend configuration
            assert "front-end" in config, "Frontend configuration missing"
            assert "solidjs" in config["front-end"], "SolidJS frontend not configured"
            
            # Verify database configuration
            assert config.get("postgresql") == True, "PostgreSQL not configured"
            
            # Verify code generation flags
            assert config.get("controller") == True, "Controller generation not enabled"
            assert config.get("model") == True, "Model generation not enabled"
            assert config.get("interface") == True, "Interface generation not enabled"
        
        # Check setup.php
        setup_file = project_root / "setup.php"
        assert setup_file.exists(), "setup.php not found"
    
    def test_orm_relationship_modernization(self, project_root):
        """
        AC0: Verify ORM relationship modernization (Task 0.6)
        
        Requirements:
        - ORM models should use string-based relationship references
        - No __init__.py files in python/app/orm/ (Python 3.3+ implicit namespace)
        - Models should be importable directly
        - Relationships defined in 'relations' dictionary with string callbacks
        """
        orm_dir = project_root / "python" / "app" / "orm"
        
        # Check that __init__.py does NOT exist (implicit namespace packages)
        init_file = orm_dir / "__init__.py"
        assert not init_file.exists(), \
            "__init__.py should not exist in orm/ directory (Python 3.3+ implicit namespace)"
        
        # Check that model files exist and are importable
        model_files = list(orm_dir.glob("*.py"))
        assert len(model_files) > 0, "No ORM model files found"
        
        # Verify at least one model file contains relationship definitions
        farm_model = orm_dir / "farm.py"
        if farm_model.exists():
            with open(farm_model, 'r') as f:
                content = f.read()
                # Should have relations dictionary with string-based callbacks
                assert "relations = {" in content, \
                    "Farm model should have relations dictionary"
                assert "'callback':" in content, \
                    "Farm model should use string-based callbacks in relations"


class TestSchemaValidation:
    """Test specific schema validation requirements"""
    
    @pytest.fixture
    def schema_dir(self):
        """Get schema directory"""
        project_root = Path(__file__).parent.parent.parent
        return project_root / "database" / "Model"
    
    def test_user_schema(self, schema_dir):
        """Verify user schema has authentication fields"""
        user_schema_file = schema_dir / "user.json"
        assert user_schema_file.exists(), "user.json schema not found"
        
        with open(user_schema_file, 'r') as f:
            schema = json.load(f)
            
            # Check for authentication-related fields in data
            data_fields = schema.get("data", [])
            field_names = [field.get("name") for field in data_fields]
            
            # Should have email or phone for authentication
            has_auth_field = any(field in field_names for field in ["email", "phone", "cognito_user_id"])
            assert has_auth_field, "User schema should have authentication fields"
    
    def test_farm_schema(self, schema_dir):
        """Verify farm schema has location and soil fields"""
        farm_schema_file = schema_dir / "farm.json"
        assert farm_schema_file.exists(), "farm.json schema not found"
        
        with open(farm_schema_file, 'r') as f:
            schema = json.load(f)
            
            data_fields = schema.get("data", [])
            field_names = [field.get("name") for field in data_fields]
            
            # Should have location fields
            assert any("state" in name.lower() for name in field_names), \
                "Farm schema should have state field"
            assert any("district" in name.lower() for name in field_names), \
                "Farm schema should have district field"
    
    def test_annual_strategy_schema(self, schema_dir):
        """Verify annual_strategy schema exists for core MVP feature"""
        strategy_schema_file = schema_dir / "annual_strategy.json"
        assert strategy_schema_file.exists(), \
            "annual_strategy.json schema not found - required for MVP core feature"
        
        with open(strategy_schema_file, 'r') as f:
            schema = json.load(f)
            
            # Should have data fields for storing strategy
            data_fields = schema.get("data", [])
            assert len(data_fields) > 0, "Annual strategy schema should have data fields"
    
    def test_marketplace_listing_schema(self, schema_dir):
        """Verify marketplace_listing schema exists"""
        listing_schema_file = schema_dir / "marketplace_listing.json"
        assert listing_schema_file.exists(), \
            "marketplace_listing.json schema not found - required for marketplace feature"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
