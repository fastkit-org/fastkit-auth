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

class TestVerifyToken:

    @pytest.mark.asyncio
    async def test_verify_valid_token(self, service, mock_valid_token):
        service.repository.first = AsyncMock(return_value=mock_valid_token)

        result = await service.verify_token("ABC12345", TokenType.EMAIL_VERIFICATION)

        assert result == mock_valid_token
        service.repository.first.assert_called_once_with(
            token="ABC12345", type=TokenType.EMAIL_VERIFICATION
        )

    @pytest.mark.asyncio
    async def test_verify_token_not_found_raises(self, service):
        service.repository.first = AsyncMock(return_value=None)

        with pytest.raises(Exception):
            await service.verify_token("NOTFOUND", TokenType.EMAIL_VERIFICATION)

    @pytest.mark.asyncio
    async def test_verify_expired_token_raises_and_deletes(self, service, mock_expired_token):
        service.repository.first = AsyncMock(return_value=mock_expired_token)
        service.repository.delete = AsyncMock()

        with pytest.raises(Exception):
            await service.verify_token("EXPIRED1", TokenType.EMAIL_VERIFICATION)

        service.repository.delete.assert_called_once_with(mock_expired_token.id)

    @pytest.mark.asyncio
    async def test_verify_token_checks_correct_type(self, service, mock_valid_token):
        service.repository.first = AsyncMock(return_value=mock_valid_token)

        await service.verify_token("ABC12345", TokenType.EMAIL_VERIFICATION)

        service.repository.first.assert_called_once_with(
            token="ABC12345", type=TokenType.EMAIL_VERIFICATION
        )

    @pytest.mark.asyncio
    async def test_verify_token_wrong_type_not_found(self, service):
        service.repository.first = AsyncMock(return_value=None)

        with pytest.raises(Exception):
            await service.verify_token("ABC12345", TokenType.PASSWORD_RESET)

class TestTokenType:

    def test_email_verification_value(self):
        assert TokenType.EMAIL_VERIFICATION.value == "email_verification"

    def test_password_reset_value(self):
        assert TokenType.PASSWORD_RESET.value == "password_reset"

    def test_enum_is_string(self):
        assert isinstance(TokenType.EMAIL_VERIFICATION, str)
        assert isinstance(TokenType.PASSWORD_RESET, str)
