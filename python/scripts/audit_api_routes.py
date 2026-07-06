import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path to import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

def audit_routes():
    # 1. Get all backend routes
    backend_routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', None)
            backend_routes.append({
                'path': route.path,
                'methods': list(methods) if methods else []
            })
    
    # 2. Read api-registry.json
    registry_path = Path(__file__).parent.parent.parent / 'solidjs' / 'src' / 'config' / 'api-registry.json'
    if not registry_path.exists():
        print(f"Error: Registry not found at {registry_path}")
        return

    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    base_url_path = "/api/v1" # Standard prefix in main.py
    
    print(f"--- API Route Audit ---")
    print(f"Total backend routes found: {len(backend_routes)}")
    
    discrepancies = []
    
    for category, endpoints in registry.get('endpoints', {}).items():
        for name, path in endpoints.items():
            # Handle standard prefixing logic from main.py
            # Most routes are included with prefix=settings.API_V1_STR
            # Some are root level like /health
            
            full_path = path
            if not path.startswith('/api/v1') and not path.startswith('/health'):
                full_path = f"/api/v1{path}"
            
            # Normalize path for comparison (handling path variables like {id})
            is_present = False
            for br in backend_routes:
                # Basic path match
                if br['path'] == full_path:
                    is_present = True
                    break
                # Match matches with variables
                if '{' in full_path:
                    # Very simple regex-like check
                    normalized_full = full_path.replace('{', '').replace('}', '')
                    normalized_br = br['path'].replace('{', '').replace('}', '')
                    if normalized_full == normalized_br:
                        is_present = True
                        break

            if not is_present:
                discrepancies.append(f"MISSING: {category}.{name} -> {full_path}")
    
    if discrepancies:
        print("\nDiscrepancies found:")
        for d in discrepancies:
            print(f"  {d}")
    else:
        print("\nNo discrepancies found! All registry endpoints exist in backend.")

if __name__ == "__main__":
    audit_routes()
