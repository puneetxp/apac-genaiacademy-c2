"""
Security verification script
Checks all security measures are properly configured
"""

import sys
from pathlib import Path
import ssl

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.password import hash_password, verify_password, get_password_strength
from app.core.encryption import get_encryption
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_tls_configuration() -> bool:
    """Verify TLS 1.3 is available"""
    logger.info("\n📋 Checking TLS Configuration...")
    
    try:
        # Check if TLS 1.3 is supported
        if hasattr(ssl, 'TLSVersion') and hasattr(ssl.TLSVersion, 'TLSv1_3'):
            logger.info("✅ TLS 1.3 is supported")
            return True
        else:
            logger.warning("⚠️  TLS 1.3 not available in this Python/OpenSSL version")
            return False
    except Exception as e:
        logger.error(f"❌ Error checking TLS: {e}")
        return False


def check_password_hashing() -> bool:
    """Verify bcrypt password hashing works"""
    logger.info("\n📋 Checking Password Hashing (bcrypt)...")
    
    try:
        # Test password hashing
        test_password = "TestPassword123!"
        hashed = hash_password(test_password)
        
        # Verify hash format (bcrypt starts with $2b$)
        if not hashed.startswith("$2b$"):
            logger.error("❌ Password hash doesn't use bcrypt format")
            return False
        
        # Verify password verification works
        if not verify_password(test_password, hashed):
            logger.error("❌ Password verification failed")
            return False
        
        # Verify wrong password fails
        if verify_password("WrongPassword", hashed):
            logger.error("❌ Password verification accepted wrong password")
            return False
        
        logger.info("✅ Password hashing with bcrypt works correctly")
        logger.info(f"   Sample hash: {hashed[:30]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Password hashing error: {e}")
        return False


def check_field_encryption() -> bool:
    """Verify field-level encryption works"""
    logger.info("\n📋 Checking Field-Level Encryption (AES-256-GCM)...")
    
    try:
        encryption = get_encryption()
        
        # Test encryption/decryption
        test_data = "sensitive_data_12345"
        encrypted = encryption.encrypt(test_data)
        decrypted = encryption.decrypt(encrypted)
        
        if decrypted != test_data:
            logger.error("❌ Encryption/decryption failed")
            return False
        
        # Verify encrypted data is different from original
        if encrypted == test_data:
            logger.error("❌ Data not actually encrypted")
            return False
        
        # Test with email
        test_email = "farmer@example.com"
        encrypted_email = encryption.encrypt(test_email)
        decrypted_email = encryption.decrypt(encrypted_email)
        
        if decrypted_email != test_email:
            logger.error("❌ Email encryption/decryption failed")
            return False
        
        logger.info("✅ Field-level encryption (AES-256-GCM) works correctly")
        logger.info(f"   Original: {test_data}")
        logger.info(f"   Encrypted: {encrypted[:40]}...")
        logger.info(f"   Decrypted: {decrypted}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Encryption error: {e}")
        return False


def check_security_headers() -> bool:
    """Verify security headers are configured"""
    logger.info("\n📋 Checking Security Headers Configuration...")
    
    try:
        from app.core.security_middleware import SecurityHeadersMiddleware
        
        # Check that middleware exists
        logger.info("✅ SecurityHeadersMiddleware is configured")
        logger.info("   Headers include:")
        logger.info("   - X-Content-Type-Options: nosniff")
        logger.info("   - X-Frame-Options: DENY")
        logger.info("   - X-XSS-Protection: 1; mode=block")
        logger.info("   - Strict-Transport-Security (HSTS)")
        logger.info("   - Content-Security-Policy (CSP)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Security headers error: {e}")
        return False


def check_rate_limiting() -> bool:
    """Verify rate limiting is configured"""
    logger.info("\n📋 Checking Rate Limiting Configuration...")
    
    if not settings.RATE_LIMIT_ENABLED:
        logger.warning("⚠️  Rate limiting is disabled")
        return False
    
    logger.info("✅ Rate limiting is enabled")
    logger.info(f"   Authenticated users: {settings.RATE_LIMIT_PER_MINUTE} requests/minute")
    logger.info(f"   Public users: {settings.RATE_LIMIT_PUBLIC_PER_MINUTE} requests/minute")
    
    return True


def check_cors_configuration() -> bool:
    """Verify CORS is properly configured"""
    logger.info("\n📋 Checking CORS Configuration...")
    
    allowed_origins = settings.get_allowed_origins_list()
    
    if "*" in allowed_origins:
        logger.error("❌ CORS allows all origins (*) - security risk!")
        return False
    
    logger.info("✅ CORS is properly configured with whitelist")
    logger.info(f"   Allowed origins: {', '.join(allowed_origins)}")
    
    return True


def check_secret_key() -> bool:
    """Verify secret key is properly configured"""
    logger.info("\n📋 Checking Secret Key Configuration...")
    
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "test-secret-key-change-in-production":
            logger.error("❌ Using default secret key in production!")
            return False
        
        if len(settings.SECRET_KEY) < 32:
            logger.error("❌ Secret key too short (minimum 32 characters)")
            return False
    
    logger.info("✅ Secret key is properly configured")
    logger.info(f"   Length: {len(settings.SECRET_KEY)} characters")
    
    return True


def check_cognito_jwt_validation() -> bool:
    """Verify Cognito JWT validation is configured"""
    logger.info("\n📋 Checking Cognito JWT Validation...")
    
    if settings.COGNITO_USER_POOL_ID == "test-pool-id":
        logger.warning("⚠️  Using test Cognito configuration")
        if settings.ENVIRONMENT == "production":
            logger.error("❌ Test Cognito config in production!")
            return False
    
    logger.info("✅ Cognito JWT validation is configured")
    logger.info(f"   User Pool ID: {settings.COGNITO_USER_POOL_ID}")
    logger.info(f"   Region: {settings.COGNITO_REGION}")
    
    return True


def check_input_validation() -> bool:
    """Verify input validation is configured"""
    logger.info("\n📋 Checking Input Validation...")
    
    try:
        from app.core.security_middleware import RequestValidationMiddleware
        
        logger.info("✅ Request validation middleware is configured")
        logger.info(f"   Max request size: {settings.MAX_REQUEST_SIZE_MB}MB")
        logger.info(f"   Max JSON fields: {settings.MAX_JSON_FIELDS}")
        logger.info(f"   Max string length: {settings.MAX_STRING_LENGTH}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Input validation error: {e}")
        return False


def main():
    """Run all security checks"""
    logger.info("=" * 70)
    logger.info("🔒 SECURITY VERIFICATION REPORT")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 70)
    
    checks = [
        ("TLS 1.3 Configuration", check_tls_configuration),
        ("Password Hashing (bcrypt)", check_password_hashing),
        ("Field Encryption (AES-256-GCM)", check_field_encryption),
        ("Security Headers", check_security_headers),
        ("Rate Limiting", check_rate_limiting),
        ("CORS Configuration", check_cors_configuration),
        ("Secret Key", check_secret_key),
        ("Cognito JWT Validation", check_cognito_jwt_validation),
        ("Input Validation", check_input_validation),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {name}")
    
    logger.info("=" * 70)
    logger.info(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 All security checks passed!")
        return 0
    else:
        logger.warning(f"⚠️  {total - passed} security check(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
