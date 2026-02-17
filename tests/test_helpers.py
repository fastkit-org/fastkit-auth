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