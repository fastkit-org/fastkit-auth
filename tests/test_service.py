import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastkit_auth.authentication.service import AuthService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    with patch('fastkit_auth.authentication.service.UserService') as MockUserService:
        svc = AuthService(mock_session)
        svc.user_service = MockUserService.return_value
        yield svc


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    user.email = "test@example.com"
    user.first_name = "John"
    user.last_name = "Doe"
    user.is_active = True
    user.is_verified = True
    user.hashed_password = "$2b$12$hashedpassword"
    return user

# ─── authenticate ─────────────────────────────────────────────────────────────

class TestAuthenticate:

    @pytest.mark.asyncio
    async def test_authenticate_success(self, service, mock_user):
        service.user_service.find_row = AsyncMock(return_value=mock_user)

        with patch('fastkit_auth.authentication.service.PasswordHelper') as MockPH, \
             patch('fastkit_auth.authentication.service.JwtHelper') as MockJWT:
            MockPH.verify.return_value = True
            MockJWT.create_access_token.return_value = "access-token"
            MockJWT.create_refresh_token.return_value = "refresh-token"

            result = await service.authenticate("test@example.com", "password123")

        assert result["access_token"] == "access-token"
        assert result["refresh_token"] == "refresh-token"
        assert result["token_type"] == "bearer"
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["id"] == str(mock_user.id)

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, service):
        service.user_service.find_row = AsyncMock(return_value=None)

        with pytest.raises(Exception):
            await service.authenticate("nonexistent@example.com", "password")

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, service, mock_user):
        mock_user.is_active = False
        service.user_service.find_row = AsyncMock(return_value=mock_user)

        with pytest.raises(Exception):
            await service.authenticate("test@example.com", "password")

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, service, mock_user):
        service.user_service.find_row = AsyncMock(return_value=mock_user)

        with patch('fastkit_auth.authentication.service.PasswordHelper') as MockPH:
            MockPH.verify.return_value = False

            with pytest.raises(Exception):
                await service.authenticate("test@example.com", "wrongpassword")

    @pytest.mark.asyncio
    async def test_authenticate_returns_correct_user_fields(self, service, mock_user):
        service.user_service.find_row = AsyncMock(return_value=mock_user)

        with patch('fastkit_auth.authentication.service.PasswordHelper') as MockPH, \
             patch('fastkit_auth.authentication.service.JwtHelper') as MockJWT:
            MockPH.verify.return_value = True
            MockJWT.create_access_token.return_value = "at"
            MockJWT.create_refresh_token.return_value = "rt"

            result = await service.authenticate("test@example.com", "password")

        user_data = result["user"]
        assert "id" in user_data
        assert "email" in user_data
        assert "first_name" in user_data
        assert "last_name" in user_data
        assert "is_verified" in user_data
        assert "hashed_password" not in user_data

    @pytest.mark.asyncio
    async def test_authenticate_token_contains_user_id(self, service, mock_user):
        service.user_service.find_row = AsyncMock(return_value=mock_user)

        with patch('fastkit_auth.authentication.service.PasswordHelper') as MockPH, \
             patch('fastkit_auth.authentication.service.JwtHelper') as MockJWT:
            MockPH.verify.return_value = True
            MockJWT.create_access_token.return_value = "at"
            MockJWT.create_refresh_token.return_value = "rt"

            await service.authenticate("test@example.com", "password")

        MockJWT.create_access_token.assert_called_once_with({"sub": str(mock_user.id)})
        MockJWT.create_refresh_token.assert_called_once_with({"sub": str(mock_user.id)})

# ─── reset_password ───────────────────────────────────────────────────────────

class TestResetPassword:

    @pytest.mark.asyncio
    async def test_reset_password_success(self, service, mock_user):
        service.user_service.find_row = AsyncMock(return_value=mock_user)
        service.user_service.reset_password = AsyncMock()

        await service.reset_password("test@example.com")

        service.user_service.reset_password.assert_called_once_with(mock_user)

    @pytest.mark.asyncio
    async def test_reset_password_user_not_found(self, service):
        service.user_service.find_row = AsyncMock(return_value=None)

        with pytest.raises(Exception):
            await service.reset_password("nonexistent@example.com")

    @pytest.mark.asyncio
    async def test_reset_password_calls_find_with_email(self, service, mock_user):
        service.user_service.find_row = AsyncMock(return_value=mock_user)
        service.user_service.reset_password = AsyncMock()

        await service.reset_password("test@example.com")

        service.user_service.find_row.assert_called_once_with(email="test@example.com")