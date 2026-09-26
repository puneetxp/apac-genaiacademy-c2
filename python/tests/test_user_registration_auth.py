"""
Property-based tests for user registration and authentication
Tests Property 1: User Registration and Authentication

**Validates: Requirements AC1**
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.services.cognito_service import CognitoService


# Custom strategies for user credentials
@st.composite
def valid_email(draw):
    """Generate valid email addresses"""
    username = draw(
        st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
        )
    )
    domain = draw(
        st.sampled_from(
            [
                "gmail.com",
                "yahoo.com",
                "outlook.com",
                "hotmail.com",
                "example.com",
                "test.com",
                "mail.com",
            ]
        )
    )
    return f"{username}@{domain}"


@st.composite
def valid_phone_number(draw):
    """Generate valid Indian phone numbers"""
    # Indian mobile numbers start with 6, 7, 8, or 9
    first_digit = draw(st.sampled_from(["6", "7", "8", "9"]))
    remaining_digits = draw(
        st.text(
            min_size=9,
            max_size=9,
            alphabet=st.characters(min_codepoint=48, max_codepoint=57),  # 0-9
        )
    )
    return f"+91{first_digit}{remaining_digits}"


@st.composite
def valid_password(draw):
    """Generate valid passwords (8+ chars, mixed case, numbers, special chars)"""
    # Ensure password meets Cognito requirements
    length = draw(st.integers(min_value=8, max_value=20))

    # Build password with required character types
    lowercase = draw(st.text(min_size=1, max_size=3, alphabet="abcdefghijklmnopqrstuvwxyz"))
    uppercase = draw(st.text(min_size=1, max_size=3, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    digits = draw(st.text(min_size=1, max_size=3, alphabet="0123456789"))
    special = draw(st.text(min_size=1, max_size=2, alphabet="!@#$%^&*"))

    # Combine and pad to desired length
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
def valid_user_credentials(draw):
    """Generate complete valid user credentials"""
    username = draw(
        st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
        )
    )

    email = draw(valid_email())
    phone = draw(valid_phone_number())
    password = draw(valid_password())

    full_name = draw(
        st.text(
            min_size=2,
            max_size=50,
            alphabet=st.characters(min_codepoint=65, max_codepoint=122),  # A-Z, a-z
        )
    )

    return {
        "username": username,
        "email": email,
        "phone_number": phone,
        "password": password,
        "full_name": full_name,
    }


def create_mock_cognito_signup_response(user_sub: str = "test-user-sub-123") -> Dict[str, Any]:
    """Create a valid mock Cognito sign up response"""
    return {
        "UserSub": user_sub,
        "UserConfirmed": False,
        "CodeDeliveryDetails": {
            "Destination": "t***@e***.com",
            "DeliveryMedium": "EMAIL",
            "AttributeName": "email",
        },
    }


def create_mock_cognito_signin_response() -> Dict[str, Any]:
    """Create a valid mock Cognito sign in response with tokens"""
    return {
        "AuthenticationResult": {
            "AccessToken": "mock-access-token-" + "x" * 100,
            "IdToken": "mock-id-token-" + "y" * 100,
            "RefreshToken": "mock-refresh-token-" + "z" * 100,
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
        }
    }


class TestUserRegistrationAuthentication:
    """
    Property 1: User Registration and Authentication

    Test that for any valid user credentials (email/phone + password),
    registration creates Cognito account and authentication returns tokens.
    """

    @given(credentials=valid_user_credentials())
    @settings(
        max_examples=200,
        deadline=10000,  # 10 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_user_registration_creates_cognito_account(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any valid user credentials (email/phone + password),
        registration should create a Cognito account and return user_sub.
        """
        # Arrange
        service = CognitoService()
        mock_response = create_mock_cognito_signup_response()

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            mock_client.sign_up.return_value = mock_response

            # Act
            result = service.sign_up(
                username=credentials["username"],
                password=credentials["password"],
                email=credentials["email"],
                phone_number=credentials["phone_number"],
                full_name=credentials["full_name"],
            )

            # Assert: sign_up was called exactly once
            assert (
                mock_client.sign_up.call_count == 1
            ), f"Expected exactly 1 Cognito sign_up call, but got {mock_client.sign_up.call_count}"

            # Assert: sign_up was called with correct parameters
            call_args = mock_client.sign_up.call_args
            assert call_args is not None, "Cognito sign_up was not called"

            # Verify username and password were passed
            assert (
                call_args.kwargs["Username"] == credentials["username"]
            ), "Username not passed correctly to Cognito"
            assert (
                call_args.kwargs["Password"] == credentials["password"]
            ), "Password not passed correctly to Cognito"

            # Verify user attributes contain email, phone, and name
            user_attributes = call_args.kwargs["UserAttributes"]
            attr_dict = {attr["Name"]: attr["Value"] for attr in user_attributes}

            assert "email" in attr_dict, "Email attribute missing from sign_up call"
            assert (
                attr_dict["email"] == credentials["email"]
            ), f"Email mismatch: expected {credentials['email']}, got {attr_dict['email']}"

            assert "phone_number" in attr_dict, "Phone number attribute missing from sign_up call"
            assert (
                attr_dict["phone_number"] == credentials["phone_number"]
            ), f"Phone mismatch: expected {credentials['phone_number']}, got {attr_dict['phone_number']}"

            assert "name" in attr_dict, "Name attribute missing from sign_up call"
            assert (
                attr_dict["name"] == credentials["full_name"]
            ), f"Name mismatch: expected {credentials['full_name']}, got {attr_dict['name']}"

            # Assert: Result contains user_sub
            assert result is not None, "Sign up result was None"
            assert "user_sub" in result, "user_sub missing from sign up result"
            assert (
                result["user_sub"] == mock_response["UserSub"]
            ), f"user_sub mismatch: expected {mock_response['UserSub']}, got {result['user_sub']}"

            # Assert: Result contains confirmation status
            assert "user_confirmed" in result, "user_confirmed missing from sign up result"
            assert isinstance(result["user_confirmed"], bool), "user_confirmed should be a boolean"

    @given(credentials=valid_user_credentials())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_authentication_returns_all_tokens(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any valid user credentials, authentication should return
        access token, refresh token, and ID token.
        """
        # Arrange
        service = CognitoService()
        mock_response = create_mock_cognito_signin_response()

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            mock_client.initiate_auth.return_value = mock_response

            # Act
            result = service.sign_in(
                username=credentials["username"], password=credentials["password"]
            )

            # Assert: initiate_auth was called exactly once
            assert (
                mock_client.initiate_auth.call_count == 1
            ), f"Expected exactly 1 Cognito initiate_auth call, but got {mock_client.initiate_auth.call_count}"

            # Assert: initiate_auth was called with correct auth flow
            call_args = mock_client.initiate_auth.call_args
            assert call_args is not None, "Cognito initiate_auth was not called"
            assert call_args.kwargs["AuthFlow"] == "USER_PASSWORD_AUTH", "Incorrect auth flow used"

            # Verify username and password in auth parameters
            auth_params = call_args.kwargs["AuthParameters"]
            assert (
                auth_params["USERNAME"] == credentials["username"]
            ), "Username not passed correctly to authentication"
            assert (
                auth_params["PASSWORD"] == credentials["password"]
            ), "Password not passed correctly to authentication"

            # Assert: Result contains access_token
            assert result is not None, "Sign in result was None"
            assert "access_token" in result, "access_token missing from sign in result"
            assert isinstance(result["access_token"], str), "access_token should be a string"
            assert len(result["access_token"]) > 0, "access_token should not be empty"

            # Assert: Result contains id_token
            assert "id_token" in result, "id_token missing from sign in result"
            assert isinstance(result["id_token"], str), "id_token should be a string"
            assert len(result["id_token"]) > 0, "id_token should not be empty"

            # Assert: Result contains refresh_token
            assert "refresh_token" in result, "refresh_token missing from sign in result"
            assert isinstance(result["refresh_token"], str), "refresh_token should be a string"
            assert len(result["refresh_token"]) > 0, "refresh_token should not be empty"

            # Assert: Result contains expires_in
            assert "expires_in" in result, "expires_in missing from sign in result"
            assert isinstance(result["expires_in"], int), "expires_in should be an integer"
            assert result["expires_in"] > 0, "expires_in should be positive"

            # Assert: Result contains token_type
            assert "token_type" in result, "token_type missing from sign in result"
            assert (
                result["token_type"] == "Bearer"
            ), f"Expected token_type 'Bearer', got '{result['token_type']}'"

    @given(credentials=valid_user_credentials())
    @settings(
        max_examples=100,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_registration_and_authentication_flow(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any valid user credentials, the complete flow of
        registration -> confirmation -> authentication should work correctly.
        """
        # Arrange
        service = CognitoService()
        signup_response = create_mock_cognito_signup_response()
        signin_response = create_mock_cognito_signin_response()

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            # Setup mock responses for the flow
            mock_client.sign_up.return_value = signup_response
            mock_client.confirm_sign_up.return_value = {}
            mock_client.initiate_auth.return_value = signin_response

            # Act: Step 1 - Registration
            signup_result = service.sign_up(
                username=credentials["username"],
                password=credentials["password"],
                email=credentials["email"],
                phone_number=credentials["phone_number"],
                full_name=credentials["full_name"],
            )

            # Assert: Registration successful
            assert signup_result is not None
            assert "user_sub" in signup_result

            # Act: Step 2 - Confirmation
            confirmation_result = service.confirm_sign_up(
                username=credentials["username"], confirmation_code="123456"
            )

            # Assert: Confirmation successful
            assert confirmation_result is True

            # Act: Step 3 - Authentication
            signin_result = service.sign_in(
                username=credentials["username"], password=credentials["password"]
            )

            # Assert: Authentication successful with all tokens
            assert signin_result is not None
            assert "access_token" in signin_result
            assert "id_token" in signin_result
            assert "refresh_token" in signin_result

            # Assert: All three operations were called
            assert mock_client.sign_up.call_count == 1
            assert mock_client.confirm_sign_up.call_count == 1
            assert mock_client.initiate_auth.call_count == 1

    @given(credentials=valid_user_credentials())
    @settings(
        max_examples=100,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_token_refresh_maintains_authentication(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any authenticated user with a refresh token,
        token refresh should return new access and ID tokens.
        """
        # Arrange
        service = CognitoService()
        refresh_response = {
            "AuthenticationResult": {
                "AccessToken": "new-mock-access-token-" + "a" * 100,
                "IdToken": "new-mock-id-token-" + "b" * 100,
                "ExpiresIn": 3600,
            }
        }

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            mock_client.initiate_auth.return_value = refresh_response

            # Act
            result = service.refresh_token(
                username=credentials["username"], refresh_token="mock-refresh-token-xyz"
            )

            # Assert: initiate_auth was called with REFRESH_TOKEN_AUTH flow
            assert mock_client.initiate_auth.call_count == 1
            call_args = mock_client.initiate_auth.call_args
            assert (
                call_args.kwargs["AuthFlow"] == "REFRESH_TOKEN_AUTH"
            ), "Incorrect auth flow for token refresh"

            # Assert: Refresh token was passed
            auth_params = call_args.kwargs["AuthParameters"]
            assert "REFRESH_TOKEN" in auth_params, "Refresh token not passed"

            # Assert: New tokens returned
            assert result is not None
            assert "access_token" in result, "New access_token missing"
            assert "id_token" in result, "New id_token missing"
            assert "expires_in" in result, "expires_in missing"

            # Assert: Tokens are different from original (new tokens)
            assert result["access_token"].startswith(
                "new-mock-access-token"
            ), "Access token was not refreshed"
            assert result["id_token"].startswith("new-mock-id-token"), "ID token was not refreshed"

    def test_registration_with_duplicate_username_fails(self):
        """
        **Validates: Requirements AC1**

        Test that registration with duplicate username fails appropriately.
        """
        # Arrange
        service = CognitoService()

        # Mock the Cognito client to simulate duplicate username error
        with patch.object(service, "client") as mock_client:
            from botocore.exceptions import ClientError

            mock_client.sign_up.side_effect = ClientError(
                {"Error": {"Code": "UsernameExistsException", "Message": "User already exists"}},
                "SignUp",
            )

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                service.sign_up(
                    username="existinguser",
                    password="ValidPass123!",
                    email="test@example.com",
                    phone_number="+919876543210",
                    full_name="Test User",
                )

            assert "Sign up failed" in str(exc_info.value)

    def test_authentication_with_invalid_credentials_fails(self):
        """
        **Validates: Requirements AC1**

        Test that authentication with invalid credentials fails appropriately.
        """
        # Arrange
        service = CognitoService()

        # Mock the Cognito client to simulate invalid credentials
        with patch.object(service, "client") as mock_client:
            from botocore.exceptions import ClientError

            mock_client.initiate_auth.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "NotAuthorizedException",
                        "Message": "Incorrect username or password",
                    }
                },
                "InitiateAuth",
            )

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                service.sign_in(username="testuser", password="WrongPassword123!")

            assert "Sign in failed" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
