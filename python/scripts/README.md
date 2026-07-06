# Python Scripts

## API Registry Generator

### generate_api_registry_simple.py

Generates a centralized API endpoint registry for the frontend.

**Usage**:
```bash
python3 scripts/generate_api_registry_simple.py
```

**Output**:
- `../../solidjs/src/config/api-registry.json` - All endpoint definitions
- `../../solidjs/src/config/api-registry.ts` - TypeScript helpers

**When to Run**:
- After adding new API endpoints
- After modifying existing endpoint paths
- After changing API versioning

**What It Does**:
1. Reads endpoint definitions from the script
2. Generates JSON registry with 114+ endpoints
3. Creates TypeScript helper functions
4. Provides type-safe access for frontend

### generate_api_registry.py

Advanced version that introspects FastAPI routes (requires working venv).

**Note**: Use `generate_api_registry_simple.py` for now as it's more reliable.

## Other Scripts

Add documentation for other scripts here as they are created.
