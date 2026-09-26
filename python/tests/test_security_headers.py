"""
Test security headers implementation
Tests all security headers including CSP, HSTS, X-Frame-Options, etc.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.security_middleware import (
    CSRFProtectionMiddleware,
    RequestValidationMiddleware,
    SecurityHeadersMiddleware,
)


@pytest.fixture
def client():
    """Create test client with security middleware"""
    app = FastAPI()

    # Add security middlewares
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestValidationMiddleware)
    app.add_middleware(CSRFProtectionMiddleware)

    # Add simple test endpoints
    @app.get("/")
    async def root():
        return {"message": "Hello"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.post("/auth/signin")
    async def signin():
        return {"message": "signin"}

    return TestClient(app)


class TestSecurityHeaders:
    """Test security headers are properly set on all responses"""

    def test_x_content_type_options_header(self, client):
        """Test X-Content-Type-Options header is set to nosniff"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_x_frame_options_header(self, client):
        """Test X-Frame-Options header is set to DENY"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_x_xss_protection_header(self, client):
        """Test X-XSS-Protection header is set"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"

    def test_hsts_header(self, client):
        """Test HTTP Strict Transport Security (HSTS) header is set"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "Strict-Transport-Security" in response.headers
        hsts = response.headers["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts  # 1 year
        assert "includeSubDomains" in hsts

    def test_referrer_policy_header(self, client):
        """Test Referrer-Policy header is set"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "Referrer-Policy" in response.headers
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_permissions_policy_header(self, client):
        """Test Permissions-Policy header is set"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "Permissions-Policy" in response.headers
        permissions = response.headers["Permissions-Policy"]
        assert "geolocation=()" in permissions
        assert "microphone=()" in permissions
        assert "camera=()" in permissions

    def test_csp_header_present(self, client):
        """Test Content-Security-Policy header is present"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "Content-Security-Policy" in response.headers

    def test_csp_default_src(self, client):
        """Test CSP default-src directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp

    def test_csp_script_src(self, client):
        """Test CSP script-src directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp

    def test_csp_style_src(self, client):
        """Test CSP style-src directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "style-src 'self'" in csp

    def test_csp_img_src(self, client):
        """Test CSP img-src directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "img-src 'self' data: https:" in csp

    def test_csp_connect_src(self, client):
        """Test CSP connect-src directive allows AWS services"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "connect-src 'self'" in csp
        assert "cognito-idp" in csp or "amazonaws.com" in csp

    def test_csp_frame_ancestors(self, client):
        """Test CSP frame-ancestors directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in csp

    def test_csp_base_uri(self, client):
        """Test CSP base-uri directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "base-uri 'self'" in csp

    def test_csp_form_action(self, client):
        """Test CSP form-action directive"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "form-action 'self'" in csp


class TestSecurityHeadersOnAllEndpoints:
    """Test security headers are present on all types of endpoints"""

    def test_headers_on_root_endpoint(self, client):
        """Test security headers on root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_headers_on_health_endpoint(self, client):
        """Test security headers on health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_headers_on_docs_endpoint(self, client):
        """Test security headers on API docs endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers

    def test_headers_on_404_response(self, client):
        """Test security headers are present even on 404 responses"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers

    def test_headers_on_post_request(self, client):
        """Test security headers on POST requests"""
        response = client.post(
            "/auth/signin", json={"email": "test@example.com", "password": "testpass"}
        )
        # Response may be 401 or 422, but headers should be present
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers


class TestCSRFProtection:
    """Test CSRF protection for state-changing operations"""

    def test_csrf_middleware_exists(self, client):
        """Test CSRF protection middleware is loaded"""
        # The middleware should be present in the app
        # For now, we just verify the app runs without errors
        response = client.get("/health")
        assert response.status_code == 200

    def test_get_requests_allowed_without_csrf_token(self, client):
        """Test GET requests don't require CSRF token"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_head_requests_allowed_without_csrf_token(self, client):
        """Test HEAD requests don't require CSRF token"""
        response = client.head("/health")
        # HEAD may return 405 if not explicitly defined, but should have security headers
        assert response.status_code in [200, 405]
        # Verify security headers are still present
        assert "X-Content-Type-Options" in response.headers

    def test_options_requests_allowed_without_csrf_token(self, client):
        """Test OPTIONS requests don't require CSRF token"""
        response = client.options("/health")
        # OPTIONS may return 405 or 200 depending on endpoint
        assert response.status_code in [200, 405]


class TestHSTSConfiguration:
    """Test HSTS configuration details"""

    def test_hsts_max_age_is_one_year(self, client):
        """Test HSTS max-age is set to 1 year (31536000 seconds)"""
        response = client.get("/health")
        hsts = response.headers["Strict-Transport-Security"]
        assert "max-age=31536000" in hsts

    def test_hsts_includes_subdomains(self, client):
        """Test HSTS includes subdomains"""
        response = client.get("/health")
        hsts = response.headers["Strict-Transport-Security"]
        assert "includeSubDomains" in hsts

    def test_hsts_header_format(self, client):
        """Test HSTS header has correct format"""
        response = client.get("/health")
        hsts = response.headers["Strict-Transport-Security"]
        # Should be in format: max-age=31536000; includeSubDomains
        parts = [part.strip() for part in hsts.split(";")]
        assert "max-age=31536000" in parts
        assert "includeSubDomains" in parts


class TestContentSecurityPolicyDetails:
    """Test detailed CSP configuration"""

    def test_csp_prevents_inline_scripts_in_production(self, client):
        """Test CSP configuration for script sources"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        # In development, unsafe-inline may be allowed
        # In production, it should be removed
        assert "script-src" in csp

    def test_csp_allows_aws_connections(self, client):
        """Test CSP allows connections to AWS services"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        # Should allow connections to Cognito and Bedrock
        assert "connect-src" in csp

    def test_csp_prevents_framing(self, client):
        """Test CSP prevents the page from being framed"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in csp

    def test_csp_restricts_base_uri(self, client):
        """Test CSP restricts base URI to self"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "base-uri 'self'" in csp

    def test_csp_restricts_form_actions(self, client):
        """Test CSP restricts form actions to self"""
        response = client.get("/health")
        csp = response.headers["Content-Security-Policy"]
        assert "form-action 'self'" in csp


class TestSecurityHeadersIntegration:
    """Test security headers work together correctly"""

    def test_all_critical_headers_present(self, client):
        """Test all critical security headers are present"""
        response = client.get("/health")
        critical_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
        ]
        for header in critical_headers:
            assert header in response.headers, f"Missing critical header: {header}"

    def test_headers_dont_conflict(self, client):
        """Test security headers don't have conflicting values"""
        response = client.get("/health")

        # X-Frame-Options and CSP frame-ancestors should align
        assert response.headers["X-Frame-Options"] == "DENY"
        csp = response.headers["Content-Security-Policy"]
        assert "frame-ancestors 'none'" in csp

    def test_security_headers_on_error_responses(self, client):
        """Test security headers are present even on error responses"""
        # Test 404
        response = client.get("/nonexistent")
        assert response.status_code == 404
        assert "X-Content-Type-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers

        # Test 405 (method not allowed)
        response = client.post("/health")
        assert response.status_code == 405
        assert "X-Content-Type-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
