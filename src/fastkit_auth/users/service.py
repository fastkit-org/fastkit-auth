from fastkit_core.services import AsyncBaseCrudService
from fastkit_core.database import AsyncRepository
from fastkit_core.i18n import _
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.users.models import User
from fastkit_auth.users.schemas import UserUpdate, UserCreate, UserResponse
from fastapi_users.password import PasswordHelper
from pydantic_core import InitErrorDetails

class UserService(AsyncBaseCrudService[User, UserCreate, UserUpdate, UserResponse]):
    def __init__(self, session: AsyncSession):
        repository = AsyncRepository(User, session)
        super().__init__(repository, response_schema=UserResponse)

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
        password_helper = PasswordHelper()
        data['hashed_password'] = password_helper.hash(data['password'])
        del data['password']
        return data