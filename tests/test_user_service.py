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

