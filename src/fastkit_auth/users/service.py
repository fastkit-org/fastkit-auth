from fastkit_core.services import AsyncBaseCrudService
from fastkit_core.database import AsyncRepository
from fastkit_core.i18n import _
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.authentication.helpers import PasswordHelper
from fastkit_auth.users.models import User
from fastkit_auth.users.schemas import UserUpdate, UserCreate, UserResponse
from pydantic_core import InitErrorDetails
from datetime import datetime, timezone
from fastkit_auth.tokens.enums import TokenType
from fastkit_auth.tokens.service import TokenService
from mailbridge import MailBridge
from fastkit_core.config import config
from typing import Sequence, Optional
from sqlalchemy.orm import Load

mailer = MailBridge(
    provider=config('app.MAIL_PROVIDER'),
    host=config('app.MAIL_SERVER'),
    port=config('app.MAIL_PORT'),
    username=config('app.MAIL_USERNAME'),
    password=config('app.MAIL_PASSWORD'),
    use_tls=config('app.MAIL_SSL_TLS'),
    from_email=config('app.MAIL_FROM')
)

class UserService(AsyncBaseCrudService[User, UserCreate, UserUpdate, UserResponse]):
    def __init__(self, session: AsyncSession):
        repository = AsyncRepository(User, session)
        self.token_service = TokenService(session)
        self.session = session
        super().__init__(repository, response_schema=UserResponse)

    async def find_row(self,
                       load_relations: Sequence[Load] | None = None,
                        **filters
                       ) -> Optional[User]:
        results = await self.repository.filter(_limit=1, _load_relations=load_relations, **filters)
        return results[0] if results else None

    async def validate_create(self, data: UserCreate) -> None:
        if await self.exists(email=data['email']):
            raise ValidationError.from_exception_data(
                'ValidationError',
                [
                    InitErrorDetails(
                        type= 'value_error',
                        loc= ('email',),
                        input= data.get('email'),
                        ctx= {'error': ValueError(_('validation.users.email_already_exists'))}
                    )
                ]
            )

    async def before_create(self, data: dict) -> dict:
        data['hashed_password'] = PasswordHelper.hash(data['password'])
        del data['password']
        return data

    async def after_create(self, instance: User) -> None:
        token = await self.token_service.create_token(
            user_id=instance.id,
            token_type=TokenType.EMAIL_VERIFICATION,
            expires_in_minutes=10
        )

        mailer.send(
            to=instance.email,
            subject=_('emails.confirm_email.subject'),
            body=_('emails.confirm_email.body',
                   None,
                   name=instance.first_name,
                   code=token.token,
                   minutes=10
                   )
        )

    async def email_confirmation(self, token_string: str) -> None:
        token = await self.token_service.verify_token(
            token_string=token_string,
            token_type=TokenType.EMAIL_VERIFICATION
        )
        await self.repository.update(id=token.user_id, data={
            'email_verified_at': datetime.now(timezone.utc),
            'is_active': True,
            'is_verified': True
        }, commit=True)
        await self.token_service.delete(id=token.id)

    async def reset_password(self, user: User) -> None:
        token = await self.token_service.create_token(
            user_id=user.id,
            token_type=TokenType.PASSWORD_RESET,
            expires_in_minutes=10
        )

        mailer.send(
            to=user.email,
            subject=_('emails.resset_password.subject'),
            body=_('emails.resset_password.body',
                   None,
                   name=user.first_name,
                   code=token.token,
                   minutes=10
                   )
        )

    async def update_password(self, token_string: str, password: str) -> None:
        token = await self.token_service.verify_token(
            token_string=token_string,
            token_type=TokenType.PASSWORD_RESET
        )

        await self.repository.update(token.user_id, data={
            'hashed_password': PasswordHelper.hash(password)
        }, commit=True)

        await self.token_service.delete(id=token.id)