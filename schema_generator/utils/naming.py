"""Naming convention utilities for code generation."""

import re
from typing import str as String


def to_snake_case(value: str) -> str:
    """
    Convert string to snake_case.
    
    Examples:
        >>> to_snake_case("FarmProfile")
        'farm_profile'
        >>> to_snake_case("user-name")
        'user_name'
        >>> to_snake_case("HTTPResponse")
        'http_response'
    
    Args:
        value: Input string in any case format
        
    Returns:
        String in snake_case format
    """
    # Replace non-alphanumeric characters with underscores
    value = re.sub(r'[^a-zA-Z0-9]+', '_', value)
    
    # Insert underscore before uppercase letters that follow lowercase letters
    value = re.sub(r'([a-z])([A-Z])', r'\1_\2', value)
    
    # Insert underscore before uppercase letters that are followed by lowercase letters
    value = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', value)
    
    # Convert to lowercase
    value = value.lower()
    
    # Remove multiple consecutive underscores
    value = re.sub(r'_+', '_', value)
    
    # Remove leading/trailing underscores
    return value.strip('_')


def to_pascal_case(value: str) -> str:
    """
    Convert string to PascalCase.
    
    Examples:
        >>> to_pascal_case("farm_profile")
        'FarmProfile'
        >>> to_pascal_case("user-name")
        'UserName'
        >>> to_pascal_case("http_response")
        'HttpResponse'
    
    Args:
        value: Input string in any case format
        
    Returns:
        String in PascalCase format
    """
    # Replace non-alphanumeric characters with spaces
    value = re.sub(r'[^a-zA-Z0-9]+', ' ', value)
    
    # Split on spaces and uppercase first letter of each word
    words = value.split()
    
    # Capitalize first letter of each word
    return ''.join(word.capitalize() for word in words if word)


def to_camel_case(value: str) -> str:
    """
    Convert string to camelCase.
    
    Examples:
        >>> to_camel_case("farm_profile")
        'farmProfile'
        >>> to_camel_case("user-name")
        'userName'
        >>> to_camel_case("HTTPResponse")
        'httpResponse'
    
    Args:
        value: Input string in any case format
        
    Returns:
        String in camelCase format
    """
    pascal = to_pascal_case(value)
    
    if not pascal:
        return ''
    
    # Lowercase the first character
    return pascal[0].lower() + pascal[1:]


def to_kebab_case(value: str) -> str:
    """
    Convert string to kebab-case.
    
    Examples:
        >>> to_kebab_case("FarmProfile")
        'farm-profile'
        >>> to_kebab_case("user_name")
        'user-name'
        >>> to_kebab_case("HTTPResponse")
        'http-response'
    
    Args:
        value: Input string in any case format
        
    Returns:
        String in kebab-case format
    """
    # First convert to snake_case
    snake = to_snake_case(value)
    
    # Replace underscores with hyphens
    return snake.replace('_', '-')
