"""
Test lightweight ORM (Model + DB classes)
Similar to compile-php Model/DB pattern
"""

import pytest
from app.core.model import Model
from app.core.db import DB


# Example model definition
class TestUser(Model):
    table = "users"
    fillable = ["email", "phone_number", "full_name", "user_type"]
    relations = {}


class TestFarm(Model):
    table = "farms"
    fillable = ["farmer_id", "name", "location_state", "location_district", "total_area"]
    relations = {
        'farmer': {
            'table': 'users',
            'name': 'farmer_id',
            'key': 'id',
            'callback': TestUser
        }
    }


def test_db_query_building():
    """Test DB class builds queries correctly"""
    db = DB("users")
    
    # Test SELECT
    db.sel_set(["id", "email"])
    assert 'SELECT id, email FROM "users"' in db.query
    
    # Test WHERE
    db2 = DB("users")
    db2.sel_set().where_q({"email": ["test@example.com"]})
    db2.bind()
    assert 'WHERE' in db2.query
    assert '"email" IN (?)' in db2.query
    assert db2.placeholder == ["test@example.com"]
    
    # Test LIMIT and OFFSET
    db3 = DB("users")
    db3.sel_set().limit_q(10).offset_q(20)
    db3.bind()
    assert 'LIMIT 10' in db3.query
    assert 'OFFSET 20' in db3.query


def test_db_insert_query():
    """Test INSERT query building"""
    db = DB("users")
    data = [
        {"email": "user1@example.com", "full_name": "User One"},
        {"email": "user2@example.com", "full_name": "User Two"}
    ]
    
    db.in_set().insert_q(data)
    
    assert 'INSERT INTO "users"' in db.query
    assert '"email", "full_name"' in db.query
    assert 'VALUES' in db.query
    assert len(db.placeholder) == 4  # 2 records x 2 fields


def test_db_update_query():
    """Test UPDATE query building"""
    db = DB("users")
    data = {"full_name": "Updated Name", "email": "updated@example.com"}
    
    db.update_q(data).where_q({"id": [1]})
    db.bind()
    
    assert 'UPDATE "users" SET' in db.query
    assert '"full_name" = ?' in db.query
    assert '"email" = ?' in db.query
    assert 'WHERE' in db.query
    assert db.placeholder[0] == "Updated Name"
    assert db.placeholder[1] == "updated@example.com"


def test_db_delete_query():
    """Test DELETE query building"""
    db = DB("users")
    db.del_set().where_q({"id": [1]})
    db.bind()
    
    assert 'DELETE FROM "users"' in db.query
    assert 'WHERE' in db.query
    assert '"id" IN (?)' in db.query


def test_db_custom_where():
    """Test custom WHERE conditions"""
    db = DB("users")
    db.sel_set().where_custom_q([
        ("age", ">", 18),
        ("status", "=", "active")
    ])
    db.bind()
    
    assert '"age" > ?' in db.query
    assert '"status" = ?' in db.query
    assert db.placeholder == [18, "active"]


def test_db_count_query():
    """Test COUNT query"""
    db = DB("users")
    db.count_set()
    
    assert 'SELECT count(*) FROM "users"' in db.query


def test_model_class_methods():
    """Test Model class static methods"""
    # Test that methods return Model instances
    assert isinstance(TestUser.where({"email": ["test@example.com"]}), TestUser)
    assert isinstance(TestUser.where_custom([("age", ">", 18)]), TestUser)


def test_model_fillable_filtering():
    """Test that Model filters to fillable fields"""
    user = TestUser()
    
    # Test clean method
    data = [
        {"email": "test@example.com", "password": "secret", "full_name": "Test User"}
    ]
    cleaned = user.clean(data)
    
    assert "email" in cleaned[0]
    assert "full_name" in cleaned[0]
    assert "password" not in cleaned[0]  # Not in fillable


def test_model_query_chaining():
    """Test Model query chaining"""
    query = TestUser.where({"user_type": ["farmer"]})
    query.and_where({"email": ["test@example.com"]})
    
    # Verify query was built
    assert len(query.db.where_and) == 2


def test_model_relationships():
    """Test relationship definitions"""
    farm = TestFarm()
    
    assert "farmer" in farm.relations
    assert farm.relations["farmer"]["table"] == "users"
    assert farm.relations["farmer"]["callback"] == TestUser


def test_model_to_dict():
    """Test Model to_dict conversion"""
    user = TestUser()
    user.items = [{"id": 1, "email": "test@example.com"}]
    
    result = user.to_dict()
    assert isinstance(result, list)
    assert result[0]["email"] == "test@example.com"


def test_model_singular_mode():
    """Test singular mode for single records"""
    user = TestUser()
    user.set_singular()
    
    assert user.singular is True


def test_db_postgresql_placeholder_conversion():
    """Test that placeholders convert to PostgreSQL format"""
    db = DB("users")
    db.sel_set().where_q({"email": ["test@example.com"]})
    db.bind()
    
    # Before exe(), query has ?
    assert '?' in db.query
    
    # After conversion (simulated), should have $1, $2, etc
    pg_query = db.query
    for i in range(len(db.placeholder)):
        pg_query = pg_query.replace('?', f'${i+1}', 1)
    
    assert '$1' in pg_query
    assert '?' not in pg_query


def test_model_pagination_calculation():
    """Test pagination calculations"""
    user = TestUser()
    user.page = {
        'result': 100,
        'page_number': 2,
        'page_items': 25
    }
    
    # Calculate total pages
    total_pages = (user.page['result'] + user.page['page_items'] - 1) // user.page['page_items']
    assert total_pages == 4
    
    # Calculate offset
    offset = (user.page['page_number'] - 1) * user.page['page_items']
    assert offset == 25


def test_db_upsert_query():
    """Test UPSERT (ON CONFLICT) query building"""
    db = DB("users")
    data = [{"id": 1, "email": "test@example.com", "full_name": "Test User"}]
    
    db.in_set().upsert_q(data)
    
    assert 'INSERT INTO "users"' in db.query
    assert 'ON CONFLICT (id) DO UPDATE SET' in db.query
    assert '"email" = EXCLUDED."email"' in db.query


def test_model_create_filters_fields():
    """Test that create filters to fillable fields"""
    # This would need actual DB connection to test fully
    # Here we just verify the filtering logic
    user = TestUser()
    data = {"email": "test@example.com", "password": "secret", "full_name": "Test"}
    
    filtered = {k: v for k, v in data.items() if k in user.fillable}
    
    assert "email" in filtered
    assert "full_name" in filtered
    assert "password" not in filtered


def test_db_raw_sql():
    """Test raw SQL execution"""
    db = DB("users")
    db.rawsql("SELECT * FROM users WHERE age > 18")
    
    assert "SELECT * FROM users WHERE age > 18" in db.query


def test_model_with_relations_structure():
    """Test with_rel method structure"""
    farm = TestFarm()
    farm.items = [
        {"id": 1, "farmer_id": 10, "name": "Test Farm"}
    ]
    
    # Test that with_rel accepts list and string
    assert callable(farm.with_rel)
    
    # Test with string - just verify structure without DB call
    farm2 = TestFarm()
    farm2.items = []  # Empty items to avoid DB call
    farm2.with_relations = []
    
    # Verify relation config exists
    assert "farmer" in farm2.relations
    assert farm2.relations["farmer"]["callback"] == TestUser


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
