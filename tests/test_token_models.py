import pytest
import string
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from fastkit_auth.tokens.models import UserToken


# ─── generate_token ───────────────────────────────────────────────────────────

class TestGenerateToken:

    def test_default_length(self):
        token = UserToken.generate_token()
        assert len(token) == 8

    def test_custom_length(self):
        token = UserToken.generate_token(length=16)
        assert len(token) == 16

    def test_contains_only_alphanumeric_uppercase(self):
        allowed = set(string.ascii_uppercase + string.digits)
        for _ in range(100):  # run multiple times due to randomness
            token = UserToken.generate_token()
            assert all(c in allowed for c in token)

    def test_no_lowercase_characters(self):
        for _ in range(100):
            token = UserToken.generate_token()
            assert token == token.upper()

    def test_generates_unique_tokens(self):
        tokens = {UserToken.generate_token() for _ in range(50)}
        # With 36^8 combinations, 50 tokens should all be unique
        assert len(tokens) == 50

    def test_length_zero(self):
        token = UserToken.generate_token(length=0)
        assert token == ""

    def test_length_one(self):
        token = UserToken.generate_token(length=1)
        assert len(token) == 1

class TestIsValid:

    def _make_token(self, expires_at: datetime) -> UserToken:
        token = MagicMock(spec=UserToken)
        token.expires_at = expires_at
        token.is_valid = UserToken.is_valid.__get__(token)
        return token

    def test_valid_token_future_expiry(self):
        token = self._make_token(datetime.now(timezone.utc) + timedelta(minutes=10))
        assert token.is_valid() is True

    def test_expired_token(self):
        token = self._make_token(datetime.now(timezone.utc) - timedelta(minutes=1))
        assert token.is_valid() is False

    def test_just_expired_token(self):
        token = self._make_token(datetime.now(timezone.utc) - timedelta(seconds=1))
        assert token.is_valid() is False

    def test_far_future_expiry(self):
        token = self._make_token(datetime.now(timezone.utc) + timedelta(days=365))
        assert token.is_valid() is True
