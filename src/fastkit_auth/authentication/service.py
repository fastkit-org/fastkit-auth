from fastkit_auth.users.service import UserService
from fastkit_auth.authentication.helpers import PasswordHelper, JwtHelper
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_core.i18n import _
from typing import Dict
from fastkit_core.validation.errors import raise_validation_error

class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_service = UserService(session)

    async def authenticate(self, email: str, password: str) -> Dict:
        user = await self.user_service.find_row(email=email)
        if user is None:
            raise_validation_error('email', _('auth.invalid_credentials'))

        if not user.is_active:
            raise_validation_error('email', _('auth.account_not_active'))

        if not PasswordHelper.verify(password, user.hashed_password):
            raise_validation_error('password', _('auth.invalid_credentials'))

        token_data = {"sub": str(user.id)}
        access_token = JwtHelper.create_access_token(token_data)
        refresh_token = JwtHelper.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_verified": user.is_verified
            }
        }

    async def reset_password(self, email: str):
        user = await self.user_service.find_row(email=email)
        if user is None:
            raise_validation_error('email', _('auth.user_does_not_exists'))

        await self.user_service.reset_password(user)
