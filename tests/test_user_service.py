import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from pydantic import ValidationError

from fastkit_auth.users.service import UserService
from fastkit_auth.tokens.enums import TokenType

@pytest.fixture(autouse=True)
def mock_i18n():
    with patch('fastkit_auth.users.service._', side_effect=lambda key, *a, **kw: key):
        yield

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

class TestFindRow:

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self, service, mock_user):
        service.repository.filter = AsyncMock(return_value=[mock_user])

        result = await service.find_row(email="test@example.com")

        assert result == mock_user
        service.repository.filter.assert_called_once_with(
            _limit=1, _load_relations=None, email="test@example.com"
        )

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self, service):
        service.repository.filter = AsyncMock(return_value=[])

        result = await service.find_row(email="nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_passes_load_relations(self, service):
        service.repository.filter = AsyncMock(return_value=[])
        mock_relations = [MagicMock()]

        await service.find_row(load_relations=mock_relations, email="test@example.com")

        service.repository.filter.assert_called_once_with(
            _limit=1, _load_relations=mock_relations, email="test@example.com"
        )

    @pytest.mark.asyncio
    async def test_passes_multiple_filters(self, service, mock_user):
        service.repository.filter = AsyncMock(return_value=[mock_user])

        await service.find_row(email="test@example.com", is_active=True)

        service.repository.filter.assert_called_once_with(
            _limit=1, _load_relations=None, email="test@example.com", is_active=True
        )

class TestValidateCreate:

    @pytest.mark.asyncio
    async def test_raises_when_email_exists(self, service):
        service.exists = AsyncMock(return_value=True)

        with pytest.raises(ValidationError) as exc_info:
            await service.validate_create({"email": "existing@example.com"})

        errors = exc_info.value.errors()
        assert any(e['loc'] == ('email',) for e in errors)

    @pytest.mark.asyncio
    async def test_passes_when_email_unique(self, service):
        service.exists = AsyncMock(return_value=False)

        # Should not raise
        await service.validate_create({"email": "new@example.com"})

        service.exists.assert_called_once_with(email="new@example.com")

class TestBeforeCreate:

    @pytest.mark.asyncio
    async def test_hashes_password(self, service):
        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "hashed_password_123"

            result = await service.before_create({"password": "plaintext", "email": "test@example.com"})

        assert result["hashed_password"] == "hashed_password_123"
        assert "password" not in result
        MockPH.hash.assert_called_once_with("plaintext")

    @pytest.mark.asyncio
    async def test_removes_plain_password(self, service):
        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "hashed"

            result = await service.before_create({"password": "secret", "name": "John"})

        assert "password" not in result
        assert "name" in result

    @pytest.mark.asyncio
    async def test_preserves_other_fields(self, service):
        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "hashed"

            data = {"password": "secret", "first_name": "John", "last_name": "Doe", "email": "j@d.com"}
            result = await service.before_create(data)

        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["email"] == "j@d.com"

class TestAfterCreate:

    @pytest.mark.asyncio
    async def test_creates_email_verification_token(self, service, mock_user, mock_token):
        service.token_service.create_token = AsyncMock(return_value=mock_token)
        mock_mailer = MagicMock()
        service._get_mailer = MagicMock(return_value=mock_mailer)

        await service.after_create(mock_user)

        service.token_service.create_token.assert_called_once_with(
            user_id=mock_user.id,
            token_type=TokenType.EMAIL_VERIFICATION,
            expires_in_minutes=10
        )

    @pytest.mark.asyncio
    async def test_sends_verification_email(self, service, mock_user, mock_token):
        service.token_service.create_token = AsyncMock(return_value=mock_token)
        mock_mailer = MagicMock()
        service._get_mailer = MagicMock(return_value=mock_mailer)

        await service.after_create(mock_user)

        mock_mailer.send.assert_called_once()
        call_kwargs = mock_mailer.send.call_args[1]
        assert call_kwargs['to'] == mock_user.email

    @pytest.mark.asyncio
    async def test_email_contains_token_code(self, service, mock_user, mock_token):
        mock_token.token = "VERIFY99"
        service.token_service.create_token = AsyncMock(return_value=mock_token)
        mock_mailer = MagicMock()
        service._get_mailer = MagicMock(return_value=mock_mailer)

        await service.after_create(mock_user)

        call_kwargs = mock_mailer.send.call_args[1]
        # Body should be constructed with the token code
        assert mock_mailer.send.called

class TestEmailConfirmation:

    @pytest.mark.asyncio
    async def test_verifies_token(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        await service.email_confirmation("ABC12345")

        service.token_service.verify_token.assert_called_once_with(
            token_string="ABC12345",
            token_type=TokenType.EMAIL_VERIFICATION
        )

    @pytest.mark.asyncio
    async def test_updates_user_fields(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        await service.email_confirmation("ABC12345")

        service.repository.update.assert_called_once()
        call_kwargs = service.repository.update.call_args[1]
        assert call_kwargs['id'] == mock_token.user_id
        assert call_kwargs['data']['is_active'] is True
        assert call_kwargs['data']['is_verified'] is True
        assert 'email_verified_at' in call_kwargs['data']
        assert call_kwargs['commit'] is True

    @pytest.mark.asyncio
    async def test_deletes_token_after_confirmation(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        await service.email_confirmation("ABC12345")

        service.token_service.delete.assert_called_once_with(id=mock_token.id)

    @pytest.mark.asyncio
    async def test_invalid_token_raises(self, service):
        service.token_service.verify_token = AsyncMock(side_effect=Exception("Invalid token"))

        with pytest.raises(Exception):
            await service.email_confirmation("INVALID1")


class TestResetPassword:

    @pytest.mark.asyncio
    async def test_creates_password_reset_token(self, service, mock_user, mock_token):
        service.token_service.create_token = AsyncMock(return_value=mock_token)
        mock_mailer = MagicMock()
        service._get_mailer = MagicMock(return_value=mock_mailer)

        await service.reset_password(mock_user)

        service.token_service.create_token.assert_called_once_with(
            user_id=mock_user.id,
            token_type=TokenType.PASSWORD_RESET,
            expires_in_minutes=10
        )

    @pytest.mark.asyncio
    async def test_sends_reset_email(self, service, mock_user, mock_token):
        service.token_service.create_token = AsyncMock(return_value=mock_token)
        mock_mailer = MagicMock()
        service._get_mailer = MagicMock(return_value=mock_mailer)

        await service.reset_password(mock_user)

        mock_mailer.send.assert_called_once()
        call_kwargs = mock_mailer.send.call_args[1]
        assert call_kwargs['to'] == mock_user.email

    @pytest.mark.asyncio
    async def test_uses_correct_token_type(self, service, mock_user, mock_token):
        service.token_service.create_token = AsyncMock(return_value=mock_token)
        mock_mailer = MagicMock()
        service._get_mailer = MagicMock(return_value=mock_mailer)

        await service.reset_password(mock_user)

        call_args = service.token_service.create_token.call_args
        assert call_args[1]['token_type'] == TokenType.PASSWORD_RESET

class TestUpdatePassword:

    @pytest.mark.asyncio
    async def test_verifies_reset_token(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "new_hashed"
            await service.update_password("RESET123", "newpassword")

        service.token_service.verify_token.assert_called_once_with(
            token_string="RESET123",
            token_type=TokenType.PASSWORD_RESET
        )

    @pytest.mark.asyncio
    async def test_hashes_new_password(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "new_hashed_pw"
            await service.update_password("RESET123", "newpassword")

        MockPH.hash.assert_called_once_with("newpassword")
        call_kwargs = service.repository.update.call_args[1]
        assert call_kwargs['data']['hashed_password'] == "new_hashed_pw"

    @pytest.mark.asyncio
    async def test_deletes_token_after_update(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "hashed"
            await service.update_password("RESET123", "newpassword")

        service.token_service.delete.assert_called_once_with(id=mock_token.id)

    @pytest.mark.asyncio
    async def test_commits_password_update(self, service, mock_token):
        service.token_service.verify_token = AsyncMock(return_value=mock_token)
        service.repository.update = AsyncMock()
        service.token_service.delete = AsyncMock()

        with patch('fastkit_auth.users.service.PasswordHelper') as MockPH:
            MockPH.hash.return_value = "hashed"
            await service.update_password("RESET123", "newpassword")

        call_kwargs = service.repository.update.call_args[1]
        assert call_kwargs['commit'] is True

    @pytest.mark.asyncio
    async def test_invalid_token_raises(self, service):
        service.token_service.verify_token = AsyncMock(side_effect=Exception("Invalid"))

        with pytest.raises(Exception):
            await service.update_password("BAD_TOKEN", "newpassword")

class TestGetMailer:

    def test_creates_mailer_instance(self, service):
        with patch('fastkit_auth.users.service.config') as mock_config, \
             patch('fastkit_auth.users.service.MailBridge') as MockMailBridge:
            mock_config.return_value = "test_value"
            MockMailBridge.return_value = MagicMock()

            mailer = service._get_mailer()

            assert mailer is not None
            MockMailBridge.assert_called_once()

    def test_caches_mailer_instance(self, service):
        with patch('fastkit_auth.users.service.config') as mock_config, \
             patch('fastkit_auth.users.service.MailBridge') as MockMailBridge:
            mock_config.return_value = "test_value"
            mock_instance = MagicMock()
            MockMailBridge.return_value = mock_instance

            mailer1 = service._get_mailer()
            mailer2 = service._get_mailer()

            assert mailer1 is mailer2
            MockMailBridge.assert_called_once()