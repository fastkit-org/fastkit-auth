import pytest
from pydantic import ValidationError
from unittest.mock import patch

from fastkit_auth.authentication.schemas import LoginRequest, ResetPasswordRequest, UpdatePassword

@pytest.fixture(autouse=True)
def mock_i18n():
    with patch('fastkit_auth.authentication.schemas._', side_effect=lambda key, *a, **kw: key):
        yield

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

# ─── UpdatePassword ───────────────────────────────────────────────────────────

class TestUpdatePassword:

    def test_valid_update(self):
        data = UpdatePassword(
            code="ABC123",
            password="StrongPass1!",
            password_confirmation="StrongPass1!"
        )
        assert data.code == "ABC123"
        assert data.password == "StrongPass1!"

    def test_passwords_dont_match(self):
        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(
                code="ABC123",
                password="StrongPass1!",
                password_confirmation="DifferentPass1!"
            )
        assert "password" in str(exc_info.value).lower()

    def test_missing_code(self):
        with pytest.raises(ValidationError):
            UpdatePassword(
                password="StrongPass1!",
                password_confirmation="StrongPass1!"
            )

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            UpdatePassword(
                code="ABC123",
                password_confirmation="StrongPass1!"
            )

    def test_missing_password_confirmation(self):
        with pytest.raises(ValidationError):
            UpdatePassword(
                code="ABC123",
                password="StrongPass1!"
            )