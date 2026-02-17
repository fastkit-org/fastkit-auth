import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from fastapi import HTTPException

from fastkit_auth.authentication.dependencies import (
    get_current_user,
    get_current_verified_user,
    get_current_superuser,
)


@pytest.fixture
def mock_credentials():
    creds = MagicMock()
    creds.credentials = "valid-bearer-token"
    return creds


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def mock_user_response():
    user = MagicMock()
    user.id = str(uuid4())
    user.email = "test@example.com"
    user.is_active = True
    user.is_verified = True
    user.is_superuser = False
    return user

# ─── get_current_user ─────────────────────────────────────────────────────────

class TestGetCurrentUser:

    @pytest.mark.asyncio
    async def test_returns_user_on_valid_token(self, mock_credentials, mock_session, mock_user_response):
        with patch('fastkit_auth.authentication.dependencies.JwtHelper') as MockJWT, \
             patch('fastkit_auth.authentication.dependencies.UserService') as MockUserSvc:
            MockJWT.verify_token.return_value = {"sub": "user-123"}
            mock_svc_instance = MockUserSvc.return_value
            mock_svc_instance.find = AsyncMock(return_value=mock_user_response)

            result = await get_current_user(mock_credentials, mock_session)

        assert result == mock_user_response

    @pytest.mark.asyncio
    async def test_raises_401_on_invalid_token(self, mock_credentials, mock_session):
        with patch('fastkit_auth.authentication.dependencies.JwtHelper') as MockJWT:
            MockJWT.verify_token.side_effect = ValueError("Token invalid")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_session)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_401_on_missing_sub(self, mock_credentials, mock_session):
        with patch('fastkit_auth.authentication.dependencies.JwtHelper') as MockJWT:
            MockJWT.verify_token.return_value = {"type": "access"}  # no "sub"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_session)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_401_on_user_not_found(self, mock_credentials, mock_session):
        with patch('fastkit_auth.authentication.dependencies.JwtHelper') as MockJWT, \
             patch('fastkit_auth.authentication.dependencies.UserService') as MockUserSvc:
            MockJWT.verify_token.return_value = {"sub": "user-123"}
            mock_svc_instance = MockUserSvc.return_value
            mock_svc_instance.find = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_session)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_raises_403_on_inactive_user(self, mock_credentials, mock_session, mock_user_response):
        mock_user_response.is_active = False

        with patch('fastkit_auth.authentication.dependencies.JwtHelper') as MockJWT, \
             patch('fastkit_auth.authentication.dependencies.UserService') as MockUserSvc:
            MockJWT.verify_token.return_value = {"sub": "user-123"}
            mock_svc_instance = MockUserSvc.return_value
            mock_svc_instance.find = AsyncMock(return_value=mock_user_response)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, mock_session)

            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_verifies_token_as_access_not_refresh(self, mock_credentials, mock_session, mock_user_response):
        with patch('fastkit_auth.authentication.dependencies.JwtHelper') as MockJWT, \
             patch('fastkit_auth.authentication.dependencies.UserService') as MockUserSvc:
            MockJWT.verify_token.return_value = {"sub": "user-123"}
            mock_svc_instance = MockUserSvc.return_value
            mock_svc_instance.find = AsyncMock(return_value=mock_user_response)

            await get_current_user(mock_credentials, mock_session)

        MockJWT.verify_token.assert_called_once_with("valid-bearer-token", refresh=False)

# ─── get_current_verified_user ────────────────────────────────────────────────

class TestGetCurrentVerifiedUser:

    @pytest.mark.asyncio
    async def test_returns_verified_user(self, mock_user_response):
        mock_user_response.is_verified = True
        result = await get_current_verified_user(mock_user_response)
        assert result == mock_user_response

    @pytest.mark.asyncio
    async def test_raises_403_on_unverified_user(self, mock_user_response):
        mock_user_response.is_verified = False

        with pytest.raises(HTTPException) as exc_info:
            await get_current_verified_user(mock_user_response)

        assert exc_info.value.status_code == 403