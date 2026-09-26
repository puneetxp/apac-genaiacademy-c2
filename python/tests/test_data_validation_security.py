"""
Property-based tests for data validation and security
Tests Property 15: Data Validation and Security

**Validates: Requirements (Non-Functional - Security)**
"""

import base64
import re
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from app.core.encryption import FieldEncryption, decrypt_field, encrypt_field, get_encryption
from app.core.security_middleware import SecurityHeadersMiddleware
from app.core.validation import (
    EnumValidator,
    InputSanitizer,
    NumericRangeValidator,
    PhoneNumberValidator,
    sanitize_input,
    validate_phone,
)


# Custom strategies for sensitive data
@st.composite
def sensitive_email(draw):
    """Generate valid email addresses"""
    username = draw(
        st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
        )
    )
    domain = draw(st.sampled_from(["gmail.com", "yahoo.com", "example.com", "farmer.in"]))
    return f"{username}@{domain}"


@st.composite
def sensitive_phone(draw):
    """Generate valid Indian phone numbers"""
    # Indian mobile numbers start with 6-9
    first_digit = draw(st.sampled_from(["6", "7", "8", "9"]))
    remaining_digits = draw(st.text(min_size=9, max_size=9, alphabet="0123456789"))
    return f"+91{first_digit}{remaining_digits}"


@st.composite
def sensitive_password(draw):
    """Generate passwords (sensitive data)"""
    length = draw(st.integers(min_value=8, max_value=30))

    # Build password with mixed characters
    lowercase = draw(st.text(min_size=1, max_size=5, alphabet="abcdefghijklmnopqrstuvwxyz"))
    uppercase = draw(st.text(min_size=1, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    digits = draw(st.text(min_size=1, max_size=5, alphabet="0123456789"))
    special = draw(st.text(min_size=1, max_size=3, alphabet="!@#$%^&*"))

    password = lowercase + uppercase + digits + special
    if len(password) < length:
        padding = draw(
            st.text(
                min_size=length - len(password),
                max_size=length - len(password),
                alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
            )
        )
        password += padding

    return password[:length]


@st.composite
def sensitive_financial_data(draw):
    """Generate financial data (prices, amounts)"""
    return draw(
        st.floats(min_value=0.01, max_value=1000000.0, allow_nan=False, allow_infinity=False)
    )


@st.composite
def sensitive_contact_info(draw):
    """Generate complete contact information"""
    return {
        "email": draw(sensitive_email()),
        "phone": draw(sensitive_phone()),
        "name": draw(
            st.text(
                min_size=2, max_size=50, alphabet=st.characters(min_codepoint=65, max_codepoint=122)
            )
        ),
        "address": draw(
            st.text(
                min_size=10,
                max_size=200,
                alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            )
        ),
    }


@st.composite
def malicious_input(draw):
    """Generate potentially malicious input patterns"""
    attack_type = draw(
        st.sampled_from(["sql_injection", "xss_script", "xss_event", "null_bytes", "html_tags"])
    )

    if attack_type == "sql_injection":
        return draw(
            st.sampled_from(
                [
                    "'; DROP TABLE users; --",
                    "1' OR '1'='1",
                    "admin'--",
                    "' UNION SELECT * FROM users--",
                ]
            )
        )
    elif attack_type == "xss_script":
        return draw(
            st.sampled_from(
                [
                    "<script>alert('xss')</script>",
                    "<script>document.cookie</script>",
                    "javascript:alert('xss')",
                ]
            )
        )
    elif attack_type == "xss_event":
        return draw(
            st.sampled_from(
                [
                    "<img src=x onerror=alert('xss')>",
                    "<body onload=alert('xss')>",
                    "<div onclick=alert('xss')>test</div>",
                ]
            )
        )
    elif attack_type == "null_bytes":
        return f"test{chr(0)}string"
    else:  # html_tags
        return draw(
            st.sampled_from(
                [
                    "<iframe src='evil.com'></iframe>",
                    "<object data='evil.swf'></object>",
                    "<embed src='evil.swf'>",
                ]
            )
        )


class TestDataValidationSecurity:
    """
    Property 15: Data Validation and Security

    Test that for any user input containing sensitive data, system validates
    format, encrypts at rest (AES-256), and transmits over HTTPS/TLS 1.3.
    """

    @given(email=sensitive_email())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_email_validation_against_schema(self, email):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any email input, system validates format against defined schema.
        """
        # Act: Validate email format
        from pydantic import BaseModel, EmailStr, ValidationError

        class EmailSchema(BaseModel):
            email: EmailStr

        # Assert: Valid emails pass validation
        try:
            validated = EmailSchema(email=email)
            assert (
                validated.email == email.lower()
            ), f"Email should be normalized to lowercase: {email} -> {validated.email}"
        except ValidationError as e:
            # If validation fails, it should be due to invalid format
            pytest.fail(f"Valid email {email} failed validation: {e}")

    @given(phone=sensitive_phone())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_phone_validation_against_schema(self, phone):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any phone number input, system validates format against
        defined schema (Indian phone number format).
        """
        # Act: Validate phone format
        validated_phone = validate_phone(phone)

        # Assert: Phone is validated and formatted correctly
        assert validated_phone.startswith("+91"), f"Phone should start with +91: {validated_phone}"
        assert (
            len(validated_phone) == 13
        ), f"Phone should be 13 characters (+91 + 10 digits): {validated_phone}"
        assert (
            validated_phone[3] in "6789"
        ), f"Indian mobile numbers should start with 6-9: {validated_phone}"

        # Assert: Only digits after +91
        digits_only = validated_phone[3:]
        assert (
            digits_only.isdigit()
        ), f"Phone should contain only digits after +91: {validated_phone}"

    @given(malicious=malicious_input())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_malicious_input_rejected_by_validation(self, malicious):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any malicious input (SQL injection, XSS), system rejects
        input during validation.
        """
        # Skip null byte test as it's sanitized (removed) rather than rejected
        if "\x00" in malicious:
            # Null bytes are removed by sanitization
            result = sanitize_input(malicious, allow_html=False)
            assert "\x00" not in result, "Null bytes should be removed"
            return

        # Act & Assert: Malicious input should be rejected
        with pytest.raises(HTTPException) as exc_info:
            sanitize_input(malicious, allow_html=False)

        # Assert: Error indicates security issue
        assert exc_info.value.status_code == 400, f"Malicious input should return 400 Bad Request"

        error_detail = exc_info.value.detail.lower()
        assert any(
            keyword in error_detail for keyword in ["injection", "xss", "invalid"]
        ), f"Error should indicate security issue: {exc_info.value.detail}"

    @given(sensitive_data=st.text(min_size=1, max_size=500))
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_sensitive_data_encrypted_at_rest_aes256(self, sensitive_data):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any sensitive data, system encrypts at rest using AES-256.
        """
        # Arrange
        encryption = get_encryption()

        # Act: Encrypt the sensitive data
        encrypted = encrypt_field(sensitive_data)

        # Assert: Data is encrypted (different from original)
        assert encrypted != sensitive_data, "Encrypted data should be different from plaintext"

        # Assert: Encrypted data is base64 encoded
        try:
            decoded = base64.b64decode(encrypted.encode("utf-8"))
            assert len(decoded) > 12, "Encrypted data should contain nonce (12 bytes) + ciphertext"
        except Exception as e:
            pytest.fail(f"Encrypted data should be valid base64: {e}")

        # Assert: Encryption uses AES-256-GCM (verify by checking key size)
        assert len(encryption.key) == 32, "Encryption key should be 256 bits (32 bytes) for AES-256"

        # Assert: Data can be decrypted back to original
        decrypted = decrypt_field(encrypted)
        assert (
            decrypted == sensitive_data
        ), f"Decrypted data should match original: {sensitive_data[:50]}..."

    @given(contact=sensitive_contact_info())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_contact_information_encrypted_at_rest(self, contact):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any contact information (email, phone), system encrypts
        at rest using AES-256.
        """
        # Arrange
        encryption = get_encryption()

        # Act: Encrypt email and phone
        encrypted_email = encrypt_field(contact["email"])
        encrypted_phone = encrypt_field(contact["phone"])

        # Assert: Email is encrypted
        assert encrypted_email != contact["email"], "Email should be encrypted"
        assert len(encrypted_email) > len(
            contact["email"]
        ), "Encrypted email should be longer (includes nonce + auth tag)"

        # Assert: Phone is encrypted
        assert encrypted_phone != contact["phone"], "Phone should be encrypted"
        assert len(encrypted_phone) > len(
            contact["phone"]
        ), "Encrypted phone should be longer (includes nonce + auth tag)"

        # Assert: Encrypted data can be decrypted
        decrypted_email = decrypt_field(encrypted_email)
        decrypted_phone = decrypt_field(encrypted_phone)

        assert decrypted_email == contact["email"], "Decrypted email should match original"
        assert decrypted_phone == contact["phone"], "Decrypted phone should match original"

    @given(password=sensitive_password())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_password_encrypted_at_rest(self, password):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any password, system encrypts at rest using AES-256.
        """
        # Arrange
        encryption = get_encryption()

        # Act: Encrypt password
        encrypted = encrypt_field(password)

        # Assert: Password is encrypted
        assert encrypted != password, "Password should be encrypted"

        # Assert: Encrypted data is base64 encoded (different format)
        try:
            decoded = base64.b64decode(encrypted.encode("utf-8"))
            assert len(decoded) > 12, "Encrypted data should contain nonce (12 bytes) + ciphertext"
        except Exception:
            pytest.fail("Encrypted password should be valid base64")

        # Assert: Encryption is reversible (for field-level encryption)
        decrypted = decrypt_field(encrypted)
        assert decrypted == password, "Decrypted password should match original"

        # Assert: Encrypted length is significantly different
        assert len(encrypted) > len(
            password
        ), "Encrypted password should be longer (includes nonce + auth tag)"

    @given(financial=sensitive_financial_data())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_financial_data_encrypted_at_rest(self, financial):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any financial data, system encrypts at rest using AES-256.
        """
        # Arrange
        encryption = get_encryption()
        financial_str = str(financial)

        # Act: Encrypt financial data
        encrypted = encrypt_field(financial_str)

        # Assert: Financial data is encrypted
        assert encrypted != financial_str, "Financial data should be encrypted"

        # Assert: Original value not visible in encrypted form
        assert (
            str(financial) not in encrypted
        ), "Original financial value should not be visible in encrypted form"

        # Assert: Can decrypt back to original
        decrypted = decrypt_field(encrypted)
        assert decrypted == financial_str, "Decrypted financial data should match original"

    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    @given(st.data())
    def test_https_tls13_security_headers_present(self, data):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any HTTP response, system includes security headers that
        enforce HTTPS/TLS 1.3 transmission.
        """
        from fastapi import FastAPI, Request, Response
        from fastapi.testclient import TestClient

        # Arrange: Create test app with security middleware
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)

        # Act: Make request
        response = client.get("/test")

        # Assert: HSTS header enforces HTTPS
        assert (
            "Strict-Transport-Security" in response.headers
        ), "Strict-Transport-Security header should be present"

        hsts_value = response.headers["Strict-Transport-Security"]
        assert "max-age=" in hsts_value, "HSTS should specify max-age"
        assert "includeSubDomains" in hsts_value, "HSTS should include subdomains"

        # Extract max-age value
        max_age_match = re.search(r"max-age=(\d+)", hsts_value)
        assert max_age_match, "HSTS should have valid max-age value"
        max_age = int(max_age_match.group(1))
        assert (
            max_age >= 31536000
        ), f"HSTS max-age should be at least 1 year (31536000 seconds), got {max_age}"

        # Assert: Other security headers present
        assert (
            "X-Content-Type-Options" in response.headers
        ), "X-Content-Type-Options header should be present"
        assert (
            response.headers["X-Content-Type-Options"] == "nosniff"
        ), "X-Content-Type-Options should be 'nosniff'"

        assert "X-Frame-Options" in response.headers, "X-Frame-Options header should be present"
        assert response.headers["X-Frame-Options"] == "DENY", "X-Frame-Options should be 'DENY'"

        assert (
            "Content-Security-Policy" in response.headers
        ), "Content-Security-Policy header should be present"

    @given(email=sensitive_email(), phone=sensitive_phone(), password=sensitive_password())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_complete_security_flow_validation_encryption_transmission(
        self, email, phone, password
    ):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any user input containing sensitive data, system performs
        complete security flow: validation -> encryption -> secure transmission.
        """
        # Step 1: Validation
        # Validate email format
        from pydantic import BaseModel, EmailStr, ValidationError

        class UserData(BaseModel):
            email: EmailStr

        try:
            validated_data = UserData(email=email)
            validated_email = validated_data.email
        except ValidationError:
            pytest.skip("Invalid email format generated")

        # Validate phone format
        validated_phone = validate_phone(phone)

        # Assert: Validation successful
        assert validated_email is not None, "Email validation should succeed"
        assert validated_phone is not None, "Phone validation should succeed"

        # Step 2: Encryption at rest (AES-256)
        encrypted_email = encrypt_field(validated_email)
        encrypted_phone = encrypt_field(validated_phone)
        encrypted_password = encrypt_field(password)

        # Assert: All sensitive fields encrypted
        assert encrypted_email != validated_email, "Email should be encrypted"
        assert encrypted_phone != validated_phone, "Phone should be encrypted"
        assert encrypted_password != password, "Password should be encrypted"

        # Assert: Encryption uses AES-256
        encryption = get_encryption()
        assert len(encryption.key) == 32, "Should use AES-256 (32-byte key)"

        # Step 3: Secure transmission (verify HTTPS/TLS headers)
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)

        @app.post("/user")
        async def create_user():
            return {
                "email": encrypted_email,
                "phone": encrypted_phone,
                "password": encrypted_password,
            }

        client = TestClient(app)
        response = client.post("/user")

        # Assert: HTTPS enforcement via HSTS
        assert "Strict-Transport-Security" in response.headers, "HSTS header should enforce HTTPS"

        # Assert: Response contains encrypted data (not plaintext)
        response_data = response.json()
        assert response_data["email"] != validated_email, "Response should contain encrypted email"
        assert response_data["phone"] != validated_phone, "Response should contain encrypted phone"
        assert response_data["password"] != password, "Response should contain encrypted password"

    @given(sensitive_data=st.text(min_size=10, max_size=100))
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_encryption_uses_unique_nonce_per_encryption(self, sensitive_data):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any sensitive data encrypted multiple times, each encryption
        uses a unique nonce (preventing replay attacks).
        """
        # Arrange
        encryption = get_encryption()

        # Act: Encrypt same data twice
        encrypted1 = encrypt_field(sensitive_data)
        encrypted2 = encrypt_field(sensitive_data)

        # Assert: Different encrypted values (due to unique nonces)
        assert (
            encrypted1 != encrypted2
        ), "Same plaintext should produce different ciphertext with unique nonces"

        # Assert: Both decrypt to same plaintext
        decrypted1 = decrypt_field(encrypted1)
        decrypted2 = decrypt_field(encrypted2)

        assert decrypted1 == sensitive_data, "First encryption should decrypt correctly"
        assert decrypted2 == sensitive_data, "Second encryption should decrypt correctly"

        # Assert: Nonces are different
        decoded1 = base64.b64decode(encrypted1.encode("utf-8"))
        decoded2 = base64.b64decode(encrypted2.encode("utf-8"))

        nonce1 = decoded1[:12]
        nonce2 = decoded2[:12]

        assert nonce1 != nonce2, "Each encryption should use a unique nonce"

    @given(
        area=st.floats(min_value=0.1, max_value=10000.0, allow_nan=False, allow_infinity=False),
        soil_type=st.sampled_from(["clay", "sandy", "loamy", "black", "red"]),
    )
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_numeric_and_enum_validation(self, area, soil_type):
        """
        **Validates: Requirements (Non-Functional - Security)**

        Property: For any numeric and enum inputs, system validates against
        defined schemas and ranges.
        """
        # Act: Validate area (numeric range)
        from app.core.validation import EnumValidator, validate_area, validate_enum

        validated_area = validate_area(area)

        # Assert: Area is validated and within range
        assert validated_area == area, f"Validated area should match input: {area}"
        assert (
            0.1 <= validated_area <= 10000.0
        ), f"Area should be within valid range: {validated_area}"

        # Act: Validate soil type (enum)
        validated_soil = validate_enum(soil_type, EnumValidator.SOIL_TYPES, "soil_type")

        # Assert: Soil type is validated
        assert (
            validated_soil == soil_type.lower()
        ), f"Validated soil type should be lowercase: {validated_soil}"
        assert (
            validated_soil in EnumValidator.SOIL_TYPES
        ), f"Soil type should be in allowed values: {validated_soil}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
