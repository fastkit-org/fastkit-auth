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
