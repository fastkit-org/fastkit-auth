import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from fastkit_auth.users.service import UserService
from fastkit_auth.tokens.enums import TokenType


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    with patch('fastkit_auth.users.service.AsyncRepository') as MockRepo, \
         patch('fastkit_auth.users.service.TokenService') as MockTokenSvc:
        svc = UserService(mock_session)
        svc.repository = MockRepo.return_value
        svc.token_service = MockTokenSvc.return_value
        yield svc


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = uuid4()
    user.email = "test@example.com"
    user.first_name = "John"
    user.last_name = "Doe"
    user.hashed_password = "$2b$12$hashed"
    user.is_active = False
    user.is_verified = False
    return user


@pytest.fixture
def mock_token():
    token = MagicMock()
    token.id = 1
    token.user_id = uuid4()
    token.token = "ABC12345"
    return token

class TestFindRow:

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self, service, mock_user):
        service.repository.filter = AsyncMock(return_value=[mock_user])

        result = await service.find_row(email="test@example.com")

        assert result == mock_user
        service.repository.filter.assert_called_once_with(
            _limit=1, _load_relations=None, email="test@example.com"
        )

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, service):
        service.repository.filter = AsyncMock(return_value=[])

        result = await service.find_row(email="nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_passes_load_relations(self, service):
        service.repository.filter = AsyncMock(return_value=[])
        mock_relations = [MagicMock()]

        await service.find_row(load_relations=mock_relations, email="test@example.com")

        service.repository.filter.assert_called_once_with(
            _limit=1, _load_relations=mock_relations, email="test@example.com"
        )

    @pytest.mark.asyncio
    async def test_passes_multiple_filters(self, service, mock_user):
        service.repository.filter = AsyncMock(return_value=[mock_user])

        await service.find_row(email="test@example.com", is_active=True)

        service.repository.filter.assert_called_once_with(
            _limit=1, _load_relations=None, email="test@example.com", is_active=True
        )

class TestValidateCreate:

    @pytest.mark.asyncio
    async def test_raises_when_email_exists(self, service):
        service.exists = AsyncMock(return_value=True)

        with pytest.raises(ValidationError) as exc_info:
            await service.validate_create({"email": "existing@example.com"})

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('email',) for e in errors)

    @pytest.mark.asyncio
    async def test_passes_when_email_unique(self, service):
        service.exists = AsyncMock(return_value=False)

        # Should not raise
        await service.validate_create({"email": "new@example.com"})

        service.exists.assert_called_once_with(email="new@example.com")

