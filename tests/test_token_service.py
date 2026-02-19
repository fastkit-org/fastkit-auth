import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from fastkit_auth.tokens.enums import TokenType
from fastkit_auth.tokens.service import TokenService


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    with patch('fastkit_auth.tokens.service.AsyncRepository') as MockRepo:
        mock_repo = MockRepo.return_value
        svc = TokenService(mock_session)
        svc.repository = mock_repo
        yield svc


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def mock_valid_token(user_id):
    token = MagicMock()
    token.id = 1
    token.user_id = user_id
    token.token = "ABC12345"
    token.type = TokenType.EMAIL_VERIFICATION
    token.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    token.is_valid.return_value = True
    return token


@pytest.fixture
def mock_expired_token(user_id):
    token = MagicMock()
    token.id = 2
    token.user_id = user_id
    token.token = "EXPIRED1"
    token.type = TokenType.EMAIL_VERIFICATION
    token.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    token.is_valid.return_value = False
    return token

class TestCreateToken:

    @pytest.mark.asyncio
    async def test_create_token_invalidates_existing(self, service, user_id):
        service.invalidate_user_tokens = AsyncMock()
        service.create = AsyncMock(return_value=MagicMock())

        await service.create_token(user_id, TokenType.EMAIL_VERIFICATION)

        service.invalidate_user_tokens.assert_called_once_with(user_id, TokenType.EMAIL_VERIFICATION)

    @pytest.mark.asyncio
    async def test_create_token_calls_create(self, service, user_id):
        service.invalidate_user_tokens = AsyncMock()
        service.create = AsyncMock(return_value=MagicMock())

        await service.create_token(user_id, TokenType.PASSWORD_RESET, expires_in_minutes=15)

        service.create.assert_called_once()
        token_data = service.create.call_args[0][0]
        assert token_data.user_id == user_id
        assert token_data.type == TokenType.PASSWORD_RESET
        assert len(token_data.token) == 8

    @pytest.mark.asyncio
    async def test_create_token_default_expiry_10_minutes(self, service, user_id):
        service.invalidate_user_tokens = AsyncMock()
        service.create = AsyncMock(return_value=MagicMock())

        await service.create_token(user_id, TokenType.EMAIL_VERIFICATION)

        token_data = service.create.call_args[0][0]
        expected = datetime.now(timezone.utc) + timedelta(minutes=10)
        assert abs((token_data.expires_at - expected).total_seconds()) < 5

    @pytest.mark.asyncio
    async def test_create_token_custom_expiry(self, service, user_id):
        service.invalidate_user_tokens = AsyncMock()
        service.create = AsyncMock(return_value=MagicMock())

        await service.create_token(user_id, TokenType.PASSWORD_RESET, expires_in_minutes=30)

        token_data = service.create.call_args[0][0]
        expected = datetime.now(timezone.utc) + timedelta(minutes=30)
        assert abs((token_data.expires_at - expected).total_seconds()) < 5

    @pytest.mark.asyncio
    async def test_create_token_returns_created_token(self, service, user_id):
        service.invalidate_user_tokens = AsyncMock()
        mock_created = MagicMock()
        service.create = AsyncMock(return_value=mock_created)

        result = await service.create_token(user_id, TokenType.EMAIL_VERIFICATION)

        assert result == mock_created

class TestInvalidateUserTokens:

    @pytest.mark.asyncio
    async def test_calls_delete_many_with_correct_filters(self, service, user_id):
        service.repository.delete_many = AsyncMock()

        await service.invalidate_user_tokens(user_id, TokenType.PASSWORD_RESET)

        service.repository.delete_many.assert_called_once_with({
            "user_id": user_id,
            "type": TokenType.PASSWORD_RESET,
        })

    @pytest.mark.asyncio
    async def test_invalidate_email_verification_tokens(self, service, user_id):
        service.repository.delete_many = AsyncMock()

        await service.invalidate_user_tokens(user_id, TokenType.EMAIL_VERIFICATION)

        service.repository.delete_many.assert_called_once_with({
            "user_id": user_id,
            "type": TokenType.EMAIL_VERIFICATION,
        })

