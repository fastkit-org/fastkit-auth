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
from fastapi import Request

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
        self.request = None
        super().__init__(repository, response_schema=UserResponse)

    def set_request(self, request: Request) -> None:
        self.request = request

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
            token_type=TokenType.EMAIL_VERIFICATION
        )

        mailer.send(
            to=instance.email,
            subject=_('emails.confirm_email.subject'),
            body=_('emails.confirm_email.body',
                   None,
                   name=instance.first_name,
                   url=self.request.url_for('auth.email_verification', token=token.token)
                   )
        )

    async def email_confirmation(self, token_string: str) -> None:
        token = await self.token_service.verify_token(
            token_string=token_string,
            token_type=TokenType.EMAIL_VERIFICATION
        )
        await self.repository.update(id=token.user_id, data={
            'email_verified_at': datetime.now(timezone.utc),
            'is_active': True
        }, commit=True)
        await self.token_service.delete(id=token.id)
