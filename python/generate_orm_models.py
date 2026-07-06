#!/usr/bin/env python3
"""
Generate Python ORM models from JSON schemas
Similar to compile-php model generation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


def load_json_schemas(schema_dir: str) -> Dict[str, Dict]:
    """Load all JSON schemas from directory"""
    schemas = {}
    schema_path = Path(schema_dir)
    
    for json_file in schema_path.glob("*.json"):
        with open(json_file, 'r') as f:
            schema = json.load(f)
            schemas[schema['name']] = schema
    
    return schemas


def find_foreign_keys(schema: Dict) -> List[Dict]:
    """Find foreign key fields in schema data"""
    foreign_keys = []
    
    for field in schema.get('data', []):
        field_name = field['name']
        # Foreign keys typically end with _id
        if field_name.endswith('_id'):
            # Extract related table name (e.g., 'service_id' -> 'service')
            related_name = field_name[:-3]  # Remove '_id'
            foreign_keys.append({
                'field': field_name,
                'related_name': related_name,
                'related_table': related_name + 's'  # Pluralize (simple)
            })
    
    return foreign_keys


def find_reverse_relations(schema_name: str, all_schemas: Dict[str, Dict]) -> List[Dict]:
    """Find tables that reference this table (reverse relationships)"""
    reverse_relations = []
    
    for other_name, other_schema in all_schemas.items():
        if other_name == schema_name:
            continue
        
        # Check if other schema has foreign key to this schema
        for field in other_schema.get('data', []):
            field_name = field['name']
            if field_name == f"{schema_name}_id":
                reverse_relations.append({
                    'related_name': other_name,
                    'related_table': other_schema['table'],
                    'foreign_key': field_name,
                    'local_key': 'id'
                })
    
    return reverse_relations


def generate_model_class(schema: Dict, all_schemas: Dict[str, Dict]) -> str:
    """Generate Python ORM model class from JSON schema"""
    
    model_name = schema['name']
    table_name = schema['table']
    
    # Get fillable fields (exclude auto-generated fields)
    fillable = []
    for field in schema.get('data', []):
        field_name = field['name']
        # Exclude auto-generated fields
        if field_name not in ['id', 'created_at', 'updated_at']:
            fillable.append(field_name)
    
    # Find foreign key relationships
    foreign_keys = find_foreign_keys(schema)
    
    # Find reverse relationships
    reverse_relations = find_reverse_relations(model_name, all_schemas)
    
    # Build relationships dict
    relations = {}
    
    # Add foreign key relationships (belongs to)
    for fk in foreign_keys:
        related_name = fk['related_name']
        related_table = fk['related_table']
        
        # Convert to class name (capitalize and remove underscores)
        class_name = ''.join(word.capitalize() for word in related_name.split('_'))
        
        relations[related_name] = {
            'table': related_table,
            'name': fk['field'],  # Foreign key in current table
            'key': 'id',          # Primary key in related table
            'callback': class_name
        }
    
    # Add reverse relationships (has many)
    for rev_rel in reverse_relations:
        related_name = rev_rel['related_name']
        related_table = rev_rel['related_table']
        
        # Convert to class name
        class_name = ''.join(word.capitalize() for word in related_name.split('_'))
        
        relations[related_name] = {
            'table': related_table,
            'name': 'id',                    # Primary key in current table
            'key': rev_rel['foreign_key'],   # Foreign key in related table
            'callback': class_name
        }
    
    # Generate class code
    class_name = ''.join(word.capitalize() for word in model_name.split('_'))
    
    code = f'''"""
Auto-generated ORM model for {table_name}
Generated from: database/Model/{model_name}.json
"""

from app.core.model import Model


class {class_name}(Model):
    """ORM model for {table_name} table"""
    
    table = "{table_name}"
    
    fillable = {fillable}
    
    relations = {{
'''
    
    # Add relationships
    for rel_name, rel_config in relations.items():
        code += f'''        '{rel_name}': {{
            'table': '{rel_config['table']}',
            'name': '{rel_config['name']}',
            'key': '{rel_config['key']}',
            'callback': None  # Will be set after all models are loaded
        }},
'''
    
    code += '''    }
'''
    
    return code


def generate_all_models(schema_dir: str, output_dir: str):
    """Generate all ORM models from JSON schemas"""
    
    # Load all schemas
    schemas = load_json_schemas(schema_dir)
    
    print(f"Found {len(schemas)} schemas")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate each model
    for schema_name, schema in schemas.items():
        model_code = generate_model_class(schema, schemas)
        
        # Write to file
        output_file = output_path / f"{schema_name}.py"
        with open(output_file, 'w') as f:
            f.write(model_code)
        
        print(f"Generated: {output_file}")
    
    # Generate __init__.py with all imports
    init_code = '''"""
Auto-generated ORM models
"""

'''
    
    for schema_name in schemas.keys():
        class_name = ''.join(word.capitalize() for word in schema_name.split('_'))
        init_code += f"from .{schema_name} import {class_name}\n"
    
    init_code += "\n# Set relationship callbacks after all models are imported\n"
    
    for schema_name, schema in schemas.items():
        class_name = ''.join(word.capitalize() for word in schema_name.split('_'))
        
        # Find relationships
        foreign_keys = find_foreign_keys(schema)
        reverse_relations = find_reverse_relations(schema_name, schemas)
        
        for fk in foreign_keys:
            related_name = fk['related_name']
            related_class = ''.join(word.capitalize() for word in related_name.split('_'))
            init_code += f"{class_name}.relations['{related_name}']['callback'] = {related_class}\n"
        
        for rev_rel in reverse_relations:
            related_name = rev_rel['related_name']
            related_class = ''.join(word.capitalize() for word in related_name.split('_'))
            init_code += f"{class_name}.relations['{related_name}']['callback'] = {related_class}\n"
    
    init_code += "\n__all__ = [\n"
    for schema_name in schemas.keys():
        class_name = ''.join(word.capitalize() for word in schema_name.split('_'))
        init_code += f"    '{class_name}',\n"
    init_code += "]\n"
    
    with open(output_path / "__init__.py", 'w') as f:
        f.write(init_code)
    
    print(f"\nGenerated __init__.py with {len(schemas)} model imports")


if __name__ == "__main__":
    import sys
    
    # Default paths
    schema_dir = "../database/Model"
    output_dir = "app/orm"
    
    if len(sys.argv) > 1:
        schema_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print(f"Schema directory: {schema_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    generate_all_models(schema_dir, output_dir)
    
    print("\n✅ ORM models generated successfully!")
    print(f"\nUsage:")
    print(f"  from app.orm import User, Farm, MarketplaceListing")
    print(f"  user = User.find(1)")
    print(f"  farms = Farm.where({{'farmer_id': [user_id]}}).get()")
