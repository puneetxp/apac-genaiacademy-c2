"""Template rendering using Jinja2 with custom filters."""

from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template

from ..utils.naming import (
    to_snake_case,
    to_pascal_case,
    to_camel_case,
    to_kebab_case,
)
from ..utils.type_mapping import (
    to_python_type,
    to_typescript_type,
    to_sql_type,
)


class TemplateRenderer:
    """
    Renders Jinja2 templates with schema data and custom filters.
    
    Attributes:
        env: Jinja2 environment with custom filters registered
    """
    
    def __init__(self, template_dir: Path):
        """
        Initialize template renderer.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        self._register_filters()
    
    def _register_filters(self) -> None:
        """Register custom Jinja2 filters for naming conventions and type mapping."""
        # Naming convention filters
        self.env.filters['snake_case'] = to_snake_case
        self.env.filters['pascal_case'] = to_pascal_case
        self.env.filters['camel_case'] = to_camel_case
        self.env.filters['kebab_case'] = to_kebab_case
        
        # Type mapping filters
        self.env.filters['python_type'] = to_python_type
        self.env.filters['typescript_type'] = to_typescript_type
        self.env.filters['sql_type'] = to_sql_type
        
        # Utility filters
        self.env.filters['quote'] = lambda x: f'"{x}"'
        self.env.filters['single_quote'] = lambda x: f"'{x}'"
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with given context.
        
        Args:
            template_name: Template file name (relative to template_dir)
            context: Template variables dictionary
            
        Returns:
            Rendered template string
            
        Raises:
            jinja2.TemplateNotFound: If template file doesn't exist
            jinja2.TemplateSyntaxError: If template has syntax errors
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with given context.
        
        Args:
            template_string: Template content as string
            context: Template variables dictionary
            
        Returns:
            Rendered template string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)
