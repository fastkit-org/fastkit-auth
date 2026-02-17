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
