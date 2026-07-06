#!/usr/bin/env python3
"""
Generate API Registry JSON from FastAPI routes
This script introspects the FastAPI application and generates a JSON file
that the frontend can use to discover all available API endpoints.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.config import settings


def extract_path_params(path: str) -> List[str]:
    """Extract path parameters from a route path"""
    import re
    return re.findall(r'\{(\w+)\}', path)


def categorize_endpoint(path: str, tags: List[str]) -> str:
    """Determine the category for an endpoint based on path and tags"""
    # Remove /api/v1 prefix
    clean_path = path.replace('/api/v1/', '').replace('/api/v1', '')
    
    # Use tags if available
    if tags:
        tag = tags[0].lower().replace(' ', '_')
        return tag
    
    # Fallback to path-based categorization
    if clean_path.startswith('auth'):
        return 'auth'
    elif clean_path.startswith('users'):
        return 'users'
    elif clean_path.startswith('farms'):
        return 'farms'
    elif clean_path.startswith('crops') or clean_path.startswith('crop-'):
        return 'crops'
    elif clean_path.startswith('annual-strategy'):
        return 'crops'
    elif clean_path.startswith('marketplace'):
        return 'marketplace'
    elif clean_path.startswith('livestock'):
        return 'livestock'
    elif clean_path.startswith('weather'):
        return 'weather'
    elif clean_path.startswith('soil'):
        return 'soil'
    elif clean_path.startswith('fertilizer'):
        return 'fertilizer'
    elif clean_path.startswith('pest-disease'):
        return 'pest_disease'
    elif clean_path.startswith('plot-'):
        return 'plot_analysis'
    elif clean_path.startswith('market-'):
        return 'market_data'
    elif clean_path.startswith('ai-quota'):
        return 'ai_quota'
    elif clean_path.startswith('address'):
        return 'address'
    elif clean_path.startswith('analytics'):
        return 'analytics'
    elif clean_path.startswith('predictive-analytics'):
        return 'predictive_analytics'
    elif clean_path.startswith('upload'):
        return 'upload'
    elif clean_path.startswith('health'):
        return 'health'
    elif clean_path.startswith('transport'):
        return 'transport'
    else:
        return 'other'


def generate_endpoint_name(path: str, method: str) -> str:
    """Generate a friendly name for an endpoint"""
    # Remove /api/v1 prefix and parameters
    clean_path = path.replace('/api/v1/', '').replace('/api/v1', '')
    
    # Remove path parameters
    import re
    clean_path = re.sub(r'/\{[^}]+\}', '', clean_path)
    
    # Split by slashes and convert to camelCase
    parts = [p for p in clean_path.split('/') if p]
    
    if not parts:
        return method.lower()
    
    # Handle common patterns
    if method == 'GET' and len(parts) == 1:
        return 'list' if not clean_path.endswith('s') else parts[0]
    elif method == 'POST' and len(parts) == 1:
        return 'create'
    elif method == 'GET' and '{' in path:
        return 'get'
    elif method == 'PUT' and '{' in path:
        return 'update'
    elif method == 'PATCH' and '{' in path:
        return 'update'
    elif method == 'DELETE' and '{' in path:
        return 'delete'
    
    # Convert to camelCase
    name = parts[0]
    for part in parts[1:]:
        name += part.capitalize()
    
    return name


def generate_api_registry() -> Dict[str, Any]:
    """Generate API registry from FastAPI routes"""
    
    registry = {
        "$schema": "./api-registry-schema.json",
        "version": "1.0.0",
        "generatedAt": None,  # Will be set when writing
        "baseUrl": "http://localhost:8000",
        "apiVersion": "v1",
        "endpoints": {}
    }
    
    # Group endpoints by category
    categorized_endpoints: Dict[str, Dict[str, Any]] = {}
    
    for route in app.routes:
        # Skip non-API routes
        if not hasattr(route, 'methods') or not hasattr(route, 'path'):
            continue
        
        path = route.path
        methods = route.methods
        
        # Skip OPTIONS method
        methods = [m for m in methods if m != 'OPTIONS']
        
        if not methods:
            continue
        
        # Get tags
        tags = []
        if hasattr(route, 'tags') and route.tags:
            tags = route.tags
        
        # Categorize endpoint
        category = categorize_endpoint(path, tags)
        
        if category not in categorized_endpoints:
            categorized_endpoints[category] = {}
        
        # Process each method
        for method in methods:
            endpoint_name = generate_endpoint_name(path, method)
            
            # Avoid duplicates by appending method if needed
            original_name = endpoint_name
            counter = 1
            while endpoint_name in categorized_endpoints[category]:
                endpoint_name = f"{original_name}{counter}"
                counter += 1
            
            categorized_endpoints[category][endpoint_name] = {
                "path": path,
                "method": method,
                "params": extract_path_params(path),
                "tags": tags
            }
    
    # Convert to simpler format for frontend (just path strings)
    simplified_endpoints = {}
    for category, endpoints in sorted(categorized_endpoints.items()):
        simplified_endpoints[category] = {}
        for name, details in sorted(endpoints.items()):
            simplified_endpoints[category][name] = details['path']
    
    registry['endpoints'] = simplified_endpoints
    
    # Add detailed endpoint information
    registry['endpointDetails'] = categorized_endpoints
    
    return registry


def main():
    """Main function to generate and save API registry"""
    print("Generating API registry from FastAPI routes...")
    
    registry = generate_api_registry()
    
    # Add generation timestamp
    from datetime import datetime
    registry['generatedAt'] = datetime.utcnow().isoformat() + 'Z'
    
    # Determine output path
    output_dir = Path(__file__).parent.parent.parent / 'solidjs' / 'src' / 'config'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'api-registry.json'
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"✓ API registry generated: {output_file}")
    print(f"✓ Found {sum(len(v) for v in registry['endpoints'].values())} endpoints")
    print(f"✓ Categories: {', '.join(sorted(registry['endpoints'].keys()))}")
    
    # Also generate TypeScript types
    generate_typescript_types(registry, output_dir)


def generate_typescript_types(registry: Dict[str, Any], output_dir: Path):
    """Generate TypeScript types for the API registry"""
    
    ts_content = """// Auto-generated TypeScript types for API Registry
// DO NOT EDIT - Generated by scripts/generate_api_registry.py

export interface ApiEndpoint {
  path: string;
  method: string;
  params: string[];
  tags: string[];
}

export interface ApiRegistry {
  $schema: string;
  version: string;
  generatedAt: string;
  baseUrl: string;
  apiVersion: string;
  endpoints: {
"""
    
    # Add endpoint categories
    for category in sorted(registry['endpoints'].keys()):
        ts_content += f"    {category}: {{\n"
        for endpoint_name in sorted(registry['endpoints'][category].keys()):
            ts_content += f"      {endpoint_name}: string;\n"
        ts_content += "    };\n"
    
    ts_content += """  };
  endpointDetails: {
"""
    
    # Add detailed endpoint types
    for category in sorted(registry['endpointDetails'].keys()):
        ts_content += f"    {category}: {{\n"
        for endpoint_name in sorted(registry['endpointDetails'][category].keys()):
            ts_content += f"      {endpoint_name}: ApiEndpoint;\n"
        ts_content += "    };\n"
    
    ts_content += """  };
}

// Helper function to build URL with parameters
export function buildUrl(template: string, params: Record<string, string | number>): string {
  let url = template;
  for (const [key, value] of Object.entries(params)) {
    url = url.replace(`{${key}}`, String(value));
  }
  return url;
}

// Helper function to get full URL
export function getFullUrl(baseUrl: string, path: string): string {
  return `${baseUrl}${path}`;
}
"""
    
    # Write TypeScript file
    ts_file = output_dir / 'api-registry.types.ts'
    with open(ts_file, 'w') as f:
        f.write(ts_content)
    
    print(f"✓ TypeScript types generated: {ts_file}")


if __name__ == '__main__':
    main()
