from fastkit_core.services import AsyncBaseCrudService
from fastkit_core.database import AsyncRepository
from fastkit_core.i18n import _
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.tokens.models import UserToken
from fastkit_auth.tokens.schemas import TokenCreate, TokenResponse
from fastkit_auth.tokens.enums import TokenType
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastkit_core.validation.errors import raise_validation_error


class TokenService(AsyncBaseCrudService[UserToken, TokenCreate, dict, TokenResponse]):
    def __init__(self, session: AsyncSession):
        repository = AsyncRepository(UserToken, session)
        super().__init__(repository, response_schema=TokenResponse)

    async def create_token(
            self,
            user_id: UUID,
            token_type: TokenType,
            expires_in_minutes: int = 10
    ) -> UserToken:
        await self.invalidate_user_tokens(user_id, token_type)

        token_data = TokenCreate(
            user_id=user_id,
            token=UserToken.generate_token(),
            type=token_type,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
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
                await self.repository.delete(token.id)
                raise_validation_error('token', _('tokens.expired'))

        return token