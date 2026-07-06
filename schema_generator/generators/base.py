"""Base generator class for all code generators."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from dataclasses import dataclass

from ..core.template_renderer import TemplateRenderer


@dataclass
class GeneratedFile:
    """Represents a generated code file."""
    path: Path
    content: str
    target: str  # 'python', 'solidjs', 'sql'
    category: str  # 'model', 'service', 'router', 'interface', 'migration'


class BaseGenerator(ABC):
    """
    Abstract base class for code generators.
    
    All target-specific generators (FastAPI, SolidJS, SQL) should inherit from this class.
    """
    
    def __init__(self, template_renderer: TemplateRenderer, output_dir: Path):
        """
        Initialize base generator.
        
        Args:
            template_renderer: Template renderer instance
            output_dir: Output directory for generated files
        """
        self.renderer = template_renderer
        self.output_dir = output_dir
    
    @abstractmethod
    def generate(self, schemas: List[any]) -> List[GeneratedFile]:
        """
        Generate code for all schemas.
        
        Args:
            schemas: List of parsed schemas
            
        Returns:
            List of generated files
        """
        pass
    
    def get_output_path(self, relative_path: str) -> Path:
        """
        Get absolute output path for a relative path.
        
        Args:
            relative_path: Relative path from output directory
            
        Returns:
            Absolute path
        """
        return self.output_dir / relative_path
