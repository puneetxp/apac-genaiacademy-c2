import sys
import os

# Add the parent directory to sys.path to import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

def test_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    expected_routes = [
        "/api/v1/auth/verify-email",
        "/api/v1/auth/resend-verification",
        "/api/v1/auth/logout"
    ]
    
    print("Checking for new routes:")
    for expected in expected_routes:
        found = any(expected in r for r in routes)
        print(f"{expected}: {'FOUND' if found else 'NOT FOUND'}")
        if not found:
            print(f"DEBUG: All routes: {routes}")

if __name__ == "__main__":
    test_routes()
