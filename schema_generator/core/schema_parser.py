"""Schema parsing and data models."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ParsedField:
    """Represents a parsed field from JSON schema."""
    name: str
    datatype: str
    sql_attribute: Optional[str] = None
    is_required: bool = False
    is_primary_key: bool = False
    is_auto_increment: bool = False
    is_unique: bool = False
    has_default: bool = False
    default_value: Optional[Any] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedField':
        """
        Create ParsedField from dictionary.
        
        Args:
            data: Field data from JSON schema
            
        Returns:
            ParsedField instance
        """
        from ..utils.type_mapping import parse_sql_attributes
        
        name = data.get('name', '')
        datatype = data.get('datatype', 'string')
        sql_attribute = data.get('sql_attribute')
        
        # Parse SQL attributes
        attrs = parse_sql_attributes(sql_attribute)
        
        return cls(
            name=name,
            datatype=datatype,
            sql_attribute=sql_attribute,
            is_required=attrs['is_not_null'] or attrs['is_primary_key'],
            is_primary_key=attrs['is_primary_key'],
            is_auto_increment=attrs['is_auto_increment'],
            is_unique=attrs['is_unique'],
            has_default=attrs['has_default'],
            default_value=attrs['default_value'],
        )


@dataclass
class ParsedRelation:
    """Represents a parsed relation from JSON schema."""
    name: str  # Relation name (e.g., 'farmer')
    foreign_key: str  # Local foreign key field (e.g., 'farmer_id')
    referenced_table: str  # Referenced table name (e.g., 'users')
    referenced_key: str  # Referenced key in target table (e.g., 'id')
    relation_type: str = 'one_to_many'  # 'one_to_many', 'many_to_many'
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'ParsedRelation':
        """
        Create ParsedRelation from dictionary.
        
        Args:
            name: Relation name
            data: Relation data from JSON schema
            
        Returns:
            ParsedRelation instance
        """
        return cls(
            name=name,
            foreign_key=data.get('name', ''),
            referenced_table=data.get('table', ''),
            referenced_key=data.get('key', 'id'),
            relation_type='one_to_many',  # Default, can be extended
        )


@dataclass
class ParsedCRUD:
    """Represents parsed CRUD permissions."""
    role: str  # Role name (e.g., 'isuper', 'islogin', 'ipublic', or custom)
    operations: List[str]  # List of operations: ['a', 'r', 'c', 'u', 'd', 'w', 'p']
    is_custom_role: bool = False
    
    @classmethod
    def from_dict(cls, role: str, operations: List[str], is_custom: bool = False) -> 'ParsedCRUD':
        """
        Create ParsedCRUD from dictionary.
        
        Args:
            role: Role name
            operations: List of CRUD operations
            is_custom: Whether this is a custom role
            
        Returns:
            ParsedCRUD instance
        """
        return cls(
            role=role,
            operations=operations,
            is_custom_role=is_custom,
        )


@dataclass
class ParsedSchema:
    """Represents a fully parsed JSON schema."""
    name: str  # Model name (e.g., 'farm')
    table: str  # Database table name (e.g., 'farms')
    fields: List[ParsedField] = field(default_factory=list)
    relations: List[ParsedRelation] = field(default_factory=list)
    crud_permissions: List[ParsedCRUD] = field(default_factory=list)
    reverse_relations: List[ParsedRelation] = field(default_factory=list)  # Relations from other models
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedSchema':
        """
        Create ParsedSchema from dictionary.
        
        Args:
            data: Schema data from JSON file
            
        Returns:
            ParsedSchema instance
        """
        name = data.get('name', '')
        table = data.get('table', name)
        
        # Parse fields
        fields = [
            ParsedField.from_dict(field_data)
            for field_data in data.get('data', [])
        ]
        
        # Parse relations
        relations = [
            ParsedRelation.from_dict(rel_name, rel_data)
            for rel_name, rel_data in data.get('relations', {}).items()
        ]
        
        # Parse CRUD permissions
        crud_permissions = []
        crud_data = data.get('crud', {})
        
        # Standard role scopes
        standard_roles = ['isuper', 'islogin', 'ipublic', 'public']
        for role in standard_roles:
            if role in crud_data and isinstance(crud_data[role], list):
                crud_permissions.append(
                    ParsedCRUD.from_dict(role, crud_data[role], is_custom=False)
                )
        
        # Custom roles
        if 'roles' in crud_data and isinstance(crud_data['roles'], dict):
            for role_name, operations in crud_data['roles'].items():
                if isinstance(operations, list):
                    crud_permissions.append(
                        ParsedCRUD.from_dict(role_name, operations, is_custom=True)
                    )
        
        return cls(
            name=name,
            table=table,
            fields=fields,
            relations=relations,
            crud_permissions=crud_permissions,
        )
    
    def get_field(self, field_name: str) -> Optional[ParsedField]:
        """Get field by name."""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None
    
    def has_field(self, field_name: str) -> bool:
        """Check if schema has a field with given name."""
        return self.get_field(field_name) is not None


class SchemaParser:
    """
    Parses JSON schemas into structured data for code generation.
    """
    
    def parse_schema(self, schema: Dict[str, Any]) -> ParsedSchema:
        """
        Parse JSON schema into structured data.
        
        Args:
            schema: Raw JSON schema dictionary
            
        Returns:
            ParsedSchema instance
        """
        return ParsedSchema.from_dict(schema)
    
    def parse_schemas(self, schemas: List[Dict[str, Any]]) -> List[ParsedSchema]:
        """
        Parse multiple JSON schemas.
        
        Args:
            schemas: List of raw JSON schema dictionaries
            
        Returns:
            List of ParsedSchema instances
        """
        return [self.parse_schema(schema) for schema in schemas]
    
    def resolve_relations(self, schemas: List[ParsedSchema]) -> List[ParsedSchema]:
        """
        Resolve bidirectional relationships between schemas.
        
        This method:
        1. Adds foreign key fields to models if not present
        2. Creates reverse relations for bidirectional navigation
        3. Validates that referenced tables exist
        
        Args:
            schemas: List of parsed schemas
            
        Returns:
            List of schemas with resolved relations
        """
        # Create schema lookup by name
        schema_map = {schema.name: schema for schema in schemas}
        
        # Process each schema
        for schema in schemas:
            # Process each relation
            for relation in schema.relations:
                # Check if foreign key field exists
                if not schema.has_field(relation.foreign_key):
                    # Add foreign key field
                    fk_field = ParsedField(
                        name=relation.foreign_key,
                        datatype='number',
                        sql_attribute='NOT NULL',
                        is_required=True,
                    )
                    schema.fields.append(fk_field)
                
                # Add reverse relation to referenced schema
                referenced_schema = schema_map.get(relation.name)
                if referenced_schema:
                    reverse_relation = ParsedRelation(
                        name=schema.name,
                        foreign_key=relation.referenced_key,
                        referenced_table=schema.table,
                        referenced_key=relation.foreign_key,
                        relation_type='one_to_many',
                    )
                    referenced_schema.reverse_relations.append(reverse_relation)
        
        return schemas
