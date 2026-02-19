import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from fastkit_auth.tokens.schemas import TokenCreate, TokenResponse
from fastkit_auth.tokens.enums import TokenType

class TestTokenCreate:

    def test_valid_token_create(self):
        uid = uuid4()
        data = TokenCreate(
            user_id=uid,
            token="ABC12345",
            type=TokenType.EMAIL_VERIFICATION,
            expires_at=datetime.now(timezone.utc)
        )
        assert data.user_id == uid
        assert data.token == "ABC12345"
        assert data.type == TokenType.EMAIL_VERIFICATION

    def test_missing_user_id(self):
        with pytest.raises(ValidationError):
            TokenCreate(
                token="ABC12345",
                type=TokenType.EMAIL_VERIFICATION,
                expires_at=datetime.now(timezone.utc)
            )

    def test_missing_token(self):
        with pytest.raises(ValidationError):
            TokenCreate(
                user_id=uuid4(),
                type=TokenType.EMAIL_VERIFICATION,
                expires_at=datetime.now(timezone.utc)
            )

    def test_missing_type(self):
        with pytest.raises(ValidationError):
            TokenCreate(
                user_id=uuid4(),
                token="ABC12345",
                expires_at=datetime.now(timezone.utc)
            )

    def test_missing_expires_at(self):
        with pytest.raises(ValidationError):
            TokenCreate(
                user_id=uuid4(),
                token="ABC12345",
                type=TokenType.EMAIL_VERIFICATION
            )

    def test_invalid_token_type(self):
        with pytest.raises(ValidationError):
            TokenCreate(
                user_id=uuid4(),
                token="ABC12345",
                type="invalid_type",
                expires_at=datetime.now(timezone.utc)
            )

    def test_accepts_password_reset_type(self):
        data = TokenCreate(
            user_id=uuid4(),
            token="XYZ99999",
            type=TokenType.PASSWORD_RESET,
            expires_at=datetime.now(timezone.utc)
        )
        assert data.type == TokenType.PASSWORD_RESET