import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError

from fastkit_auth.users.schemas import UserCreate, UserUpdate, UserResponse


class TestUserCreate:

    def test_valid_user_create(self):
        data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="StrongPass1!"
        )
        assert data.first_name == "John"
        assert data.email == "john@example.com"

    def test_missing_first_name(self):
        with pytest.raises(ValidationError):
            UserCreate(last_name="Doe", email="john@example.com", password="StrongPass1!")

    def test_missing_last_name(self):
        with pytest.raises(ValidationError):
            UserCreate(first_name="John", email="john@example.com", password="StrongPass1!")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            UserCreate(first_name="John", last_name="Doe", password="StrongPass1!")

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            UserCreate(first_name="John", last_name="Doe", email="john@example.com")

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError):
            UserCreate(
                first_name="John",
                last_name="Doe",
                email="not-an-email",
                password="StrongPass1!"
            )

    def test_no_is_superuser_field(self):
        """is_superuser should not be settable during creation"""
        data = UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="StrongPass1!"
        )
        assert not hasattr(data, 'is_superuser') or 'is_superuser' not in data.model_fields


class TestUserUpdate:

    def test_valid_update(self):
        data = UserUpdate(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        assert data.first_name == "Jane"
        assert data.email == "jane@example.com"

    def test_missing_first_name(self):
        with pytest.raises(ValidationError):
            UserUpdate(last_name="Smith", email="jane@example.com")

    def test_missing_last_name(self):
        with pytest.raises(ValidationError):
            UserUpdate(first_name="Jane", email="jane@example.com")

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            UserUpdate(first_name="Jane", last_name="Smith")

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError):
            UserUpdate(first_name="Jane", last_name="Smith", email="invalid")

    def test_no_is_superuser_field(self):
        """is_superuser should not be updatable by user"""
        assert 'is_superuser' not in UserUpdate.model_fields

    def test_no_password_field(self):
        """Password should not be changeable through profile update"""
        assert 'password' not in UserUpdate.model_fields
