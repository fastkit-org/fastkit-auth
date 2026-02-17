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
