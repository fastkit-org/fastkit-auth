from fastkit_core.services import AsyncBaseCrudService
from fastkit_core.database import AsyncRepository
from fastkit_core.i18n import _
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.users.models import User
from fastkit_auth.users.schemas import UserUpdate, UserCreate, UserResponse

class UserService(AsyncBaseCrudService[User, UserCreate, UserUpdate, UserResponse]):
    def __init__(self, session: AsyncSession):
        repository = AsyncRepository(User, session)
        super().__init__(repository, response_schema=UserResponse)

    async def validate_create(self, data: UserCreate) -> None:
        if await self.exists(email=data.email):
            raise ValueError(_('validation.users.email_already_exists'))