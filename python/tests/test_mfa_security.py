"""
Property-based tests for MFA security
Tests Property 3: MFA Security Enhancement

**Validates: Requirements AC1**
"""

from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from app.services.cognito_service import CognitoService


# Custom strategies for test data
@st.composite
def valid_username(draw):
    """Generate valid usernames"""
    return draw(
        st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(min_codepoint=97, max_codepoint=122),  # a-z
        )
    )


@st.composite
def valid_password(draw):
    """Generate valid passwords (8+ chars, mixed case, numbers, special chars)"""
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
def valid_mfa_code(draw):
    """Generate valid 6-digit MFA codes"""
    return draw(
        st.text(
            min_size=6,
            max_size=6,
            alphabet=st.characters(min_codepoint=48, max_codepoint=57),  # 0-9
        )
    )


@st.composite
def mfa_enabled_user_credentials(draw):
    """Generate credentials for a user with MFA enabled"""
    username = draw(valid_username())
    password = draw(valid_password())
    mfa_code = draw(valid_mfa_code())

    return {"username": username, "password": password, "mfa_code": mfa_code, "mfa_enabled": True}


def create_mock_mfa_challenge_response(session: str = "mock-session-123") -> Dict[str, Any]:
    """Create a mock Cognito response requiring MFA challenge"""
    return {
        "ChallengeName": "SMS_MFA",
        "Session": session,
        "ChallengeParameters": {
            "CODE_DELIVERY_DELIVERY_MEDIUM": "SMS",
            "CODE_DELIVERY_DESTINATION": "+*******3210",
        },
    }


def create_mock_mfa_success_response() -> Dict[str, Any]:
    """Create a mock successful MFA verification response with tokens"""
    return {
        "AuthenticationResult": {
            "AccessToken": "mock-access-token-after-mfa-" + "x" * 100,
            "IdToken": "mock-id-token-after-mfa-" + "y" * 100,
            "RefreshToken": "mock-refresh-token-after-mfa-" + "z" * 100,
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
        }
    }


def create_mock_no_mfa_response() -> Dict[str, Any]:
    """Create a mock response for user without MFA (direct token grant)"""
    return {
        "AuthenticationResult": {
            "AccessToken": "mock-access-token-no-mfa-" + "a" * 100,
            "IdToken": "mock-id-token-no-mfa-" + "b" * 100,
            "RefreshToken": "mock-refresh-token-no-mfa-" + "c" * 100,
            "ExpiresIn": 3600,
            "TokenType": "Bearer",
        }
    }


class TestMFASecurity:
    """
    Property 3: MFA Security Enhancement

    Test that for any user account with MFA enabled, authentication requires
    both password and MFA verification before granting access tokens.
    """

    @given(credentials=mfa_enabled_user_credentials())
    @settings(
        max_examples=200,
        deadline=10000,  # 10 seconds per test
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_mfa_enabled_user_requires_mfa_challenge(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any user account with MFA enabled, initial authentication
        with password should return MFA challenge (not tokens).
        """
        # Arrange
        service = CognitoService()
        mfa_challenge_response = create_mock_mfa_challenge_response()

        # Mock the Cognito client to return MFA challenge
        with patch.object(service, "client") as mock_client:
            mock_client.initiate_auth.return_value = mfa_challenge_response

            # Act
            result = service.sign_in(
                username=credentials["username"], password=credentials["password"]
            )

            # Assert: initiate_auth was called exactly once
            assert (
                mock_client.initiate_auth.call_count == 1
            ), f"Expected exactly 1 Cognito initiate_auth call, but got {mock_client.initiate_auth.call_count}"

            # Assert: Result contains MFA challenge (not tokens)
            assert result is not None, "Sign in result was None"
            assert "challenge" in result, "MFA challenge missing from result"
            assert (
                result["challenge"] == "SMS_MFA"
            ), f"Expected SMS_MFA challenge, got {result.get('challenge')}"

            # Assert: Session is provided for MFA verification
            assert "session" in result, "Session missing from MFA challenge response"
            assert isinstance(result["session"], str), "Session should be a string"
            assert len(result["session"]) > 0, "Session should not be empty"

            # Assert: No tokens are granted before MFA verification
            assert (
                "access_token" not in result
            ), "Access token should NOT be granted before MFA verification"
            assert (
                "id_token" not in result
            ), "ID token should NOT be granted before MFA verification"
            assert (
                "refresh_token" not in result
            ), "Refresh token should NOT be granted before MFA verification"

    @given(credentials=mfa_enabled_user_credentials())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_mfa_verification_required_for_token_grant(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any user with MFA enabled, access tokens should only be
        granted after successful MFA code verification.
        """
        # Arrange
        service = CognitoService()
        session = "mock-session-xyz-789"
        mfa_success_response = create_mock_mfa_success_response()

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            mock_client.respond_to_auth_challenge.return_value = mfa_success_response

            # Act
            result = service.respond_to_mfa_challenge(
                username=credentials["username"], session=session, mfa_code=credentials["mfa_code"]
            )

            # Assert: respond_to_auth_challenge was called exactly once
            assert (
                mock_client.respond_to_auth_challenge.call_count == 1
            ), f"Expected exactly 1 respond_to_auth_challenge call, but got {mock_client.respond_to_auth_challenge.call_count}"

            # Assert: Challenge response was called with correct parameters
            call_args = mock_client.respond_to_auth_challenge.call_args
            assert call_args is not None, "respond_to_auth_challenge was not called"
            assert call_args.kwargs["ChallengeName"] == "SMS_MFA", "Incorrect challenge name"
            assert call_args.kwargs["Session"] == session, "Session not passed correctly"

            # Verify MFA code was passed
            challenge_responses = call_args.kwargs["ChallengeResponses"]
            assert "SMS_MFA_CODE" in challenge_responses, "MFA code not passed"
            assert (
                challenge_responses["SMS_MFA_CODE"] == credentials["mfa_code"]
            ), f"MFA code mismatch: expected {credentials['mfa_code']}, got {challenge_responses['SMS_MFA_CODE']}"

            # Assert: Tokens are granted after successful MFA verification
            assert result is not None, "MFA verification result was None"
            assert "access_token" in result, "access_token missing after MFA verification"
            assert "id_token" in result, "id_token missing after MFA verification"
            assert "refresh_token" in result, "refresh_token missing after MFA verification"

            # Assert: Tokens are valid strings
            assert isinstance(result["access_token"], str), "access_token should be a string"
            assert len(result["access_token"]) > 0, "access_token should not be empty"
            assert isinstance(result["id_token"], str), "id_token should be a string"
            assert len(result["id_token"]) > 0, "id_token should not be empty"
            assert isinstance(result["refresh_token"], str), "refresh_token should be a string"
            assert len(result["refresh_token"]) > 0, "refresh_token should not be empty"

    @given(credentials=mfa_enabled_user_credentials())
    @settings(
        max_examples=200,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_complete_mfa_authentication_flow(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any user with MFA enabled, the complete authentication flow
        requires both password AND MFA code before granting tokens.
        """
        # Arrange
        service = CognitoService()
        mfa_challenge_response = create_mock_mfa_challenge_response()
        mfa_success_response = create_mock_mfa_success_response()

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            # Setup mock responses for the flow
            mock_client.initiate_auth.return_value = mfa_challenge_response
            mock_client.respond_to_auth_challenge.return_value = mfa_success_response

            # Act: Step 1 - Initial authentication with password
            signin_result = service.sign_in(
                username=credentials["username"], password=credentials["password"]
            )

            # Assert: Step 1 returns MFA challenge (not tokens)
            assert signin_result is not None
            assert "challenge" in signin_result
            assert signin_result["challenge"] == "SMS_MFA"
            assert "session" in signin_result
            assert (
                "access_token" not in signin_result
            ), "Tokens should NOT be granted before MFA verification"

            # Act: Step 2 - MFA verification
            mfa_result = service.respond_to_mfa_challenge(
                username=credentials["username"],
                session=signin_result["session"],
                mfa_code=credentials["mfa_code"],
            )

            # Assert: Step 2 grants tokens after successful MFA
            assert mfa_result is not None
            assert (
                "access_token" in mfa_result
            ), "access_token should be granted after MFA verification"
            assert "id_token" in mfa_result, "id_token should be granted after MFA verification"
            assert (
                "refresh_token" in mfa_result
            ), "refresh_token should be granted after MFA verification"

            # Assert: Both authentication steps were called
            assert (
                mock_client.initiate_auth.call_count == 1
            ), "Password authentication should be called once"
            assert (
                mock_client.respond_to_auth_challenge.call_count == 1
            ), "MFA challenge response should be called once"

    @given(username=valid_username(), password=valid_password())
    @settings(
        max_examples=100,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_user_without_mfa_gets_tokens_directly(self, username, password):
        """
        **Validates: Requirements AC1**

        Property: For any user WITHOUT MFA enabled, authentication with password
        should grant tokens directly (no MFA challenge).

        This test verifies the contrast: MFA-disabled users get tokens immediately,
        while MFA-enabled users must complete the MFA challenge.
        """
        # Arrange
        service = CognitoService()
        no_mfa_response = create_mock_no_mfa_response()

        # Mock the Cognito client to return tokens directly (no MFA)
        with patch.object(service, "client") as mock_client:
            mock_client.initiate_auth.return_value = no_mfa_response

            # Act
            result = service.sign_in(username=username, password=password)

            # Assert: Tokens are granted directly (no MFA challenge)
            assert result is not None
            assert (
                "access_token" in result
            ), "access_token should be granted directly for non-MFA users"
            assert "id_token" in result, "id_token should be granted directly for non-MFA users"
            assert (
                "refresh_token" in result
            ), "refresh_token should be granted directly for non-MFA users"

            # Assert: No MFA challenge is present
            assert (
                "challenge" not in result
            ), "MFA challenge should NOT be present for non-MFA users"
            assert (
                "session" not in result or result.get("challenge") is None
            ), "Session should NOT be present for non-MFA users (or challenge is None)"

    @given(credentials=mfa_enabled_user_credentials())
    @settings(
        max_examples=100,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_invalid_mfa_code_prevents_token_grant(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any user with MFA enabled, providing an invalid MFA code
        should prevent token grant and raise an error.
        """
        # Arrange
        service = CognitoService()
        session = "mock-session-abc-456"

        # Mock the Cognito client to simulate invalid MFA code
        with patch.object(service, "client") as mock_client:
            from botocore.exceptions import ClientError

            mock_client.respond_to_auth_challenge.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "CodeMismatchException",
                        "Message": "Invalid verification code",
                    }
                },
                "RespondToAuthChallenge",
            )

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                service.respond_to_mfa_challenge(
                    username=credentials["username"],
                    session=session,
                    mfa_code="000000",  # Invalid code
                )

            # Assert: Error message indicates MFA verification failure
            assert "MFA verification failed" in str(
                exc_info.value
            ), "Error message should indicate MFA verification failure"

    @given(credentials=mfa_enabled_user_credentials())
    @settings(
        max_examples=100,
        deadline=10000,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
    )
    def test_mfa_session_required_for_verification(self, credentials):
        """
        **Validates: Requirements AC1**

        Property: For any MFA verification attempt, a valid session from the
        initial authentication is required.
        """
        # Arrange
        service = CognitoService()
        mfa_success_response = create_mock_mfa_success_response()

        # Mock the Cognito client
        with patch.object(service, "client") as mock_client:
            mock_client.respond_to_auth_challenge.return_value = mfa_success_response

            # Act
            session = "valid-session-from-initial-auth"
            result = service.respond_to_mfa_challenge(
                username=credentials["username"], session=session, mfa_code=credentials["mfa_code"]
            )

            # Assert: Session was passed to Cognito
            call_args = mock_client.respond_to_auth_challenge.call_args
            assert call_args is not None
            assert (
                call_args.kwargs["Session"] == session
            ), "Session from initial authentication must be passed to MFA verification"

            # Assert: Verification successful with valid session
            assert result is not None
            assert "access_token" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
