from fastkit_core.services import AsyncBaseCrudService
from fastkit_core.database import AsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.users.models import User
from fastkit_auth.users.schemas import UserUpdate, UserCreate, UserResponse

class UserService(AsyncBaseCrudService[UserCreate, UserUpdate, UserResponse]):
    def __init__(self, session: AsyncSession):
        repository = AsyncRepository(User, session)
        super().__init__(repository, response_schema=UserResponse)
