import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone
import jwt

from fastkit_auth.authentication.helpers import PasswordHelper, JwtHelper


# ─── PasswordHelper Tests ────────────────────────────────────────────────────

class TestPasswordHelper:

    def test_hash_returns_string(self):
        result = PasswordHelper.hash("mypassword123")
        assert isinstance(result, str)
        assert result != "mypassword123"

    def test_hash_produces_unique_hashes(self):
        hash1 = PasswordHelper.hash("mypassword123")
        hash2 = PasswordHelper.hash("mypassword123")
        assert hash1 != hash2  # bcrypt salts should differ

    def test_verify_correct_password(self):
        hashed = PasswordHelper.hash("correctpassword")
        assert PasswordHelper.verify("correctpassword", hashed) is True

    def test_verify_incorrect_password(self):
        hashed = PasswordHelper.hash("correctpassword")
        assert PasswordHelper.verify("wrongpassword", hashed) is False

    def test_verify_empty_password(self):
        hashed = PasswordHelper.hash("somepassword")
        assert PasswordHelper.verify("", hashed) is False

    def test_needs_update_fresh_hash(self):
        hashed = PasswordHelper.hash("password")
        assert PasswordHelper.needs_update(hashed) is False

# ─── JwtHelper Tests ─────────────────────────────────────────────────────────

class TestJwtHelper:

    @pytest.fixture(autouse=True)
    def mock_config(self):
        config_values = {
            'auth.JWT_TOKEN_SECRET': 'test-access-secret',
            'auth.JWT_REFRESH_SECRET_KEY': 'test-refresh-secret',
            'auth.JWT_ALGORITHM': 'HS256',
            'auth.JWT_LIFETIME_SECONDS': 3600,
            'auth.JWT_REFRESH_LIFETIME_SECONDS': 86400,
        }
        with patch('fastkit_auth.authentication.helpers.configuration') as mock_conf:
            mock_conf.get = lambda key, default=None: config_values.get(key, default)
            yield mock_conf

    # ── create_access_token ──

    def test_create_access_token_returns_string(self):
        token = JwtHelper.create_access_token({"sub": "user-123"})
        assert isinstance(token, str)

    def test_create_access_token_contains_correct_claims(self):
        token = JwtHelper.create_access_token({"sub": "user-123"})
        payload = jwt.decode(token, "test-access-secret", algorithms=["HS256"])

        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_without_sub_raises(self):
        with pytest.raises(ValueError):
            JwtHelper.create_access_token({"role": "admin"})

    def test_create_access_token_with_empty_sub_raises(self):
        with pytest.raises(ValueError):
            JwtHelper.create_access_token({"sub": ""})

    def test_create_access_token_custom_expiry(self):
        delta = timedelta(minutes=5)
        token = JwtHelper.create_access_token({"sub": "user-123"}, expires_delta=delta)
        payload = jwt.decode(token, "test-access-secret", algorithms=["HS256"])

        expected_exp = datetime.now(timezone.utc) + delta
        actual_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert abs((expected_exp - actual_exp).total_seconds()) < 5

    def test_create_access_token_default_expiry(self):
        token = JwtHelper.create_access_token({"sub": "user-123"})
        payload = jwt.decode(token, "test-access-secret", algorithms=["HS256"])

        expected_exp = datetime.now(timezone.utc) + timedelta(seconds=3600)
        actual_exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert abs((expected_exp - actual_exp).total_seconds()) < 5

    def test_create_access_token_preserves_extra_data(self):
        token = JwtHelper.create_access_token({"sub": "user-123", "role": "admin"})
        payload = jwt.decode(token, "test-access-secret", algorithms=["HS256"])
        assert payload["role"] == "admin"

    # ── create_refresh_token ──

    def test_create_refresh_token_returns_string(self):
        token = JwtHelper.create_refresh_token({"sub": "user-123"})
        assert isinstance(token, str)

    def test_create_refresh_token_contains_correct_claims(self):
        token = JwtHelper.create_refresh_token({"sub": "user-123"})
        payload = jwt.decode(token, "test-refresh-secret", algorithms=["HS256"])

        assert payload["sub"] == "user-123"
        assert payload["type"] == "refresh"

    def test_create_refresh_token_without_sub_raises(self):
        with pytest.raises(ValueError):
            JwtHelper.create_refresh_token({"role": "admin"})

    def test_create_refresh_token_uses_different_secret(self):
        access = JwtHelper.create_access_token({"sub": "user-123"})
        refresh = JwtHelper.create_refresh_token({"sub": "user-123"})

        # Access token should not decode with refresh secret
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(access, "test-refresh-secret", algorithms=["HS256"])

        # Refresh token should not decode with access secret
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(refresh, "test-access-secret", algorithms=["HS256"])

    # ── verify_token ──

    def test_verify_access_token(self):
        token = JwtHelper.create_access_token({"sub": "user-123"})
        payload = JwtHelper.verify_token(token, refresh=False)

        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_verify_refresh_token(self):
        token = JwtHelper.create_refresh_token({"sub": "user-123"})
        payload = JwtHelper.verify_token(token, refresh=True)

        assert payload["sub"] == "user-123"
        assert payload["type"] == "refresh"

    def test_verify_expired_token_raises(self):
        token = JwtHelper.create_access_token(
            {"sub": "user-123"},
            expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(ValueError, match=".*"):
            JwtHelper.verify_token(token, refresh=False)

    def test_verify_invalid_token_raises(self):
        with pytest.raises(ValueError):
            JwtHelper.verify_token("invalid.token.string", refresh=False)

    def test_verify_access_token_with_refresh_flag_raises(self):
        token = JwtHelper.create_access_token({"sub": "user-123"})
        with pytest.raises((ValueError, jwt.InvalidSignatureError)):
            JwtHelper.verify_token(token, refresh=True)

    # ── refresh_access_token ──

    def test_refresh_access_token_success(self):
        refresh = JwtHelper.create_refresh_token({"sub": "user-123"})
        result = JwtHelper.refresh_access_token(refresh)

        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"

        # Verify the new access token is valid
        payload = JwtHelper.verify_token(result["access_token"], refresh=False)
        assert payload["sub"] == "user-123"

    def test_refresh_access_token_with_access_token_fails(self):
        access = JwtHelper.create_access_token({"sub": "user-123"})
        with pytest.raises((ValueError, jwt.InvalidSignatureError)):
            JwtHelper.refresh_access_token(access)

    def test_refresh_access_token_with_wrong_type_returns_none(self):
        # Manually create a token with type != "refresh" but signed with refresh secret
        payload = {
            "sub": "user-123",
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, "test-refresh-secret", algorithm="HS256")
        result = JwtHelper.refresh_access_token(token)
        assert result is None