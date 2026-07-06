"""Type mapping utilities for converting between different type systems."""

from typing import Dict, Any, Optional


def to_python_type(datatype: str, is_optional: bool = False) -> str:
    """
    Map JSON schema datatype to Python type hint.
    
    Args:
        datatype: JSON schema datatype (string, number, boolean, date, json)
        is_optional: Whether the field is optional
        
    Returns:
        Python type hint string
        
    Examples:
        >>> to_python_type("string")
        'str'
        >>> to_python_type("number", is_optional=True)
        'int | None'
        >>> to_python_type("json")
        'Dict[str, Any]'
    """
    type_map = {
        'string': 'str',
        'number': 'int',
        'boolean': 'bool',
        'date': 'datetime',
        'json': 'Dict[str, Any]',
    }
    
    base_type = type_map.get(datatype.lower(), 'str')
    
    if is_optional:
        return f'{base_type} | None'
    
    return base_type


def get_python_imports(datatype: str, is_optional: bool = False) -> Dict[str, list]:
    """
    Get required imports for a Python type.
    
    Args:
        datatype: JSON schema datatype
        is_optional: Whether the field is optional
        
    Returns:
        Dictionary with 'typing' and 'other' import lists
    """
    imports = {
        'typing': [],
        'other': []
    }
    
    datatype_lower = datatype.lower()
    
    if datatype_lower == 'json':
        imports['typing'].extend(['Dict', 'Any'])
    
    if datatype_lower == 'date':
        imports['other'].append('from datetime import datetime')
    
    return imports


def to_typescript_type(datatype: str) -> str:
    """
    Map JSON schema datatype to TypeScript type.
    
    Args:
        datatype: JSON schema datatype (string, number, boolean, date, json)
        
    Returns:
        TypeScript type string
        
    Examples:
        >>> to_typescript_type("string")
        'string'
        >>> to_typescript_type("number")
        'number'
        >>> to_typescript_type("json")
        'Record<string, any>'
    """
    type_map = {
        'string': 'string',
        'number': 'number',
        'boolean': 'boolean',
        'date': 'Date',
        'json': 'Record<string, any>',
    }
    
    return type_map.get(datatype.lower(), 'string')


def to_sql_type(datatype: str, sql_attribute: Optional[str] = None) -> str:
    """
    Map JSON schema datatype to PostgreSQL type.
    
    Args:
        datatype: JSON schema datatype (string, number, boolean, date, json)
        sql_attribute: Optional SQL attributes (e.g., "PRIMARY KEY AUTO_INCREMENT")
        
    Returns:
        PostgreSQL type string
        
    Examples:
        >>> to_sql_type("string")
        'VARCHAR(255)'
        >>> to_sql_type("number", "PRIMARY KEY AUTO_INCREMENT")
        'SERIAL'
        >>> to_sql_type("json")
        'JSONB'
    """
    datatype_lower = datatype.lower()
    
    # Handle AUTO_INCREMENT for number types
    if sql_attribute and 'AUTO_INCREMENT' in sql_attribute.upper():
        if datatype_lower == 'number':
            return 'SERIAL'
    
    type_map = {
        'string': 'VARCHAR(255)',
        'number': 'INTEGER',
        'boolean': 'BOOLEAN',
        'date': 'TIMESTAMP',
        'json': 'JSONB',
    }
    
    return type_map.get(datatype_lower, 'VARCHAR(255)')


def parse_sql_attributes(sql_attribute: Optional[str]) -> Dict[str, Any]:
    """
    Parse SQL attribute string into structured data.
    
    Args:
        sql_attribute: SQL attribute string (e.g., "PRIMARY KEY NOT NULL")
        
    Returns:
        Dictionary with parsed attributes
        
    Examples:
        >>> parse_sql_attributes("PRIMARY KEY AUTO_INCREMENT")
        {'is_primary_key': True, 'is_auto_increment': True, 'is_not_null': True, ...}
    """
    if not sql_attribute:
        return {
            'is_primary_key': False,
            'is_auto_increment': False,
            'is_not_null': False,
            'is_unique': False,
            'has_default': False,
            'default_value': None,
        }
    
    attr_upper = sql_attribute.upper()
    
    result = {
        'is_primary_key': 'PRIMARY KEY' in attr_upper or 'PRIMARY' in attr_upper,
        'is_auto_increment': 'AUTO_INCREMENT' in attr_upper or 'SERIAL' in attr_upper,
        'is_not_null': 'NOT NULL' in attr_upper,
        'is_unique': 'UNIQUE' in attr_upper,
        'has_default': 'DEFAULT' in attr_upper,
        'default_value': None,
    }
    
    # Extract default value if present
    if result['has_default']:
        import re
        match = re.search(r'DEFAULT\s+([^\s]+)', attr_upper)
        if match:
            result['default_value'] = match.group(1)
    
    return result
