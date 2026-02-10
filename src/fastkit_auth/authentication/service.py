from typing import Any
from fastkit_auth.users.service import UserService
from fastkit_auth.authentication.helpers import PasswordHelper, JwtHelper
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from pydantic_core import InitErrorDetails
from fastkit_core.i18n import _
from typing import Dict


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


def raise_validation_error(field: str, message: str, value: Any = None) -> None:
    raise ValidationError.from_exception_data(
        'ValidationError',
        [
            InitErrorDetails(
                type='value_error',
                loc=(field,),
                input=value,
                ctx={'error': ValueError(message)}
            )
        ]
    )