import pytest
from pydantic import ValidationError

from fastkit_auth.authentication.schemas import LoginRequest, ResetPasswordRequest, UpdatePassword


# ─── LoginRequest ─────────────────────────────────────────────────────────────

class TestLoginRequest:

    def test_valid_login(self):
        data = LoginRequest(email="test@example.com", password="password123")
        assert data.email == "test@example.com"
        assert data.password == "password123"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="password123")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(password="password123")

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="test@example.com")

    def test_empty_password_accepted(self):
        # Schema doesn't enforce min length — that's handled at service level
        data = LoginRequest(email="test@example.com", password="")
        assert data.password == ""


# ─── ResetPasswordRequest ────────────────────────────────────────────────────

class TestResetPasswordRequest:

    def test_valid_request(self):
        data = ResetPasswordRequest(email="test@example.com")
        assert data.email == "test@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            ResetPasswordRequest(email="invalid")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            ResetPasswordRequest()