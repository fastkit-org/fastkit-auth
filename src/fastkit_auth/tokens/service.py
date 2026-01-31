from typing import Any
from pydantic import ValidationError
from pydantic_core import InitErrorDetails
from fastkit_core.services import AsyncBaseCrudService
from fastkit_core.database import AsyncRepository
from fastkit_core.i18n import _
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.tokens.models import UserToken
from fastkit_auth.tokens.schemas import TokenCreate, TokenResponse
from fastkit_auth.tokens.enums import TokenType
from fastkit_auth.users.service import UserService
from fastkit_auth.users.schemas import UserUpdate
from datetime import datetime, timedelta
from uuid import UUID


class TokenService(AsyncBaseCrudService[UserToken, TokenCreate, dict, TokenResponse]):
    def __init__(self, session: AsyncSession):
        repository = AsyncRepository(UserToken, session)
        self.user_service = UserService(session)
        super().__init__(repository, response_schema=TokenResponse)

    async def create_token(
            self,
            user_id: UUID,
            token_type: TokenType,
            expires_in_hours: int = 24
    ) -> UserToken:
        await self.invalidate_user_tokens(user_id, token_type)

        token_data = TokenCreate(
            user_id=user_id,
            token=UserToken.generate_token(),
            type=token_type,
            expires_at=datetime.now() + timedelta(hours=expires_in_hours)
        )
        return await self.create(token_data)

    async def invalidate_user_tokens(self, user_id: UUID, token_type: TokenType) -> None:
         await self.repository.delete_many(
            {
                "user_id": user_id,
                "type":token_type,
            }
        )


    async def verify_token(self, token_string: str, token_type: TokenType) -> UserToken:
        token = await self.repository.first(token=token_string, type=token_type)

        if not token:
            raise_validation_error('token', _('tokens.invalid'))

        if not token.is_valid():
                raise_validation_error('token', _('tokens.expired'))

        return token

    async def email_confirmation(self, token_string:str) -> None:
        token = await self.verify_token(token_string, TokenType.EMAIL_VERIFICATION)
        await self.user_service.email_confirmation(token.user_id)
        await self.repository.delete(token.id)


    async def consume_token(self, token_string: str, token_type: TokenType) -> bool:
        token = await self.verify_token(token_string, token_type)
        await self.repository.delete(token.id)

        return  token is not None

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