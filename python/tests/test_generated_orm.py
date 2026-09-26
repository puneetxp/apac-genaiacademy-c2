"""
Test auto-generated ORM models with relationships
"""

import pytest


def test_orm_models_exist():
    """Test that ORM models were generated"""
    from app.orm.farm import Farm
    from app.orm.farm_plot import FarmPlot
    from app.orm.marketplace_listing import MarketplaceListing
    from app.orm.user import User

    assert Farm is not None
    assert User is not None
    assert MarketplaceListing is not None
    assert FarmPlot is not None


def test_farm_model_structure():
    """Test Farm model has correct structure"""
    from app.orm.farm import Farm

    # Check table name
    assert Farm.table == "farms"

    # Check fillable fields
    assert "farmer_id" in Farm.fillable
    assert "name" in Farm.fillable
    assert "state" in Farm.fillable

    # Check relationships exist - JSON schema defines it as 'user' not 'farmer'
    assert "user" in Farm.relations


def test_farm_relationships_configured():
    """Test Farm relationships are properly configured"""
    from app.orm.farm import Farm
    from app.orm.user import User

    # Check user relationship (belongs to) - JSON schema defines it as 'user' not 'farmer'
    user_rel = Farm.relations["user"]
    assert user_rel["name"] == "farmer_id"  # Foreign key in farms table
    assert user_rel["key"] == "id"  # Primary key in users table
    # Callback is a string reference
    assert user_rel["callback"] == "User"


def test_marketplace_listing_relationships():
    """Test MarketplaceListing has relationships"""
    from app.orm.marketplace_listing import MarketplaceListing

    # Check relationships
    assert "farm" in MarketplaceListing.relations
    assert "user" in MarketplaceListing.relations  # JSON schema defines it as 'user' not 'farmer'

    # Check farm relationship
    farm_rel = MarketplaceListing.relations["farm"]
    assert farm_rel["name"] == "farm_id"
    assert farm_rel["key"] == "id"


def test_user_model_structure():
    """Test User model structure"""
    from app.orm.user import User

    assert User.table == "users"
    assert "email" in User.fillable
    assert "phone" in User.fillable


def test_all_models_imported():
    """Test all models can be imported directly"""
    # Import models directly from their modules
    from app.orm.crop import Crop
    from app.orm.farm import Farm
    from app.orm.marketplace_listing import MarketplaceListing
    from app.orm.user import User

    # Verify they exist
    assert Farm is not None
    assert User is not None
    assert MarketplaceListing is not None
    assert Crop is not None


def test_model_inheritance():
    """Test models inherit from Model base class"""
    from app.core.model import Model
    from app.orm.farm import Farm

    assert issubclass(Farm, Model)


def test_model_methods_available():
    """Test models have ORM methods from base class"""
    from app.orm.farm import Farm

    # Check static methods exist
    assert hasattr(Farm, "find")
    assert hasattr(Farm, "where")
    assert hasattr(Farm, "all")
    assert hasattr(Farm, "create")
    assert hasattr(Farm, "insert")
    assert hasattr(Farm, "delete")

    # Check instance methods exist
    farm = Farm()
    assert hasattr(farm, "get")
    assert hasattr(farm, "first")
    assert hasattr(farm, "update")
    assert hasattr(farm, "with_rel")
    assert hasattr(farm, "to_dict")


def test_relationship_callback_types():
    """Test relationship callbacks are string references"""
    from app.orm.farm import Farm

    # Get callback
    callback = Farm.relations["user"]["callback"]

    # Should be a string reference to the class name
    assert isinstance(callback, str)
    assert callback == "User"


def test_bidirectional_relationships():
    """Test relationships are defined from JSON schema"""
    from app.orm.farm_plot import FarmPlot

    # FarmPlot belongs to Farm (defined in JSON)
    assert "farm" in FarmPlot.relations
    farm_rel = FarmPlot.relations["farm"]
    assert farm_rel["name"] == "farm_id"


def test_generated_models_count():
    """Test correct number of models generated"""
    import glob
    import os

    # Count .py files in orm directory (excluding __pycache__)
    orm_dir = os.path.join(os.path.dirname(__file__), "..", "app", "orm")
    model_files = glob.glob(os.path.join(orm_dir, "*.py"))

    # Should have 13 models based on JSON schemas
    assert len(model_files) == 13


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
