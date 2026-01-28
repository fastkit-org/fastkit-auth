from fastapi import APIRouter, Depends
from fastkit_core.http import success_response
from fastkit_core.database import get_async_db
from fastkit_core.i18n import _
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.users.schemas import UserCreate
from fastkit_auth.users.service import UserService
from starlette.responses import JSONResponse

registration_router = APIRouter(
    tags=['Registration']
)

def get_service(session: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(session)

@registration_router.post('/registration', name='auth.registration')
async def registration(user: UserCreate, service: UserService = Depends(get_service)) -> JSONResponse:
    data = await service.create(user.model_dump())
    return success_response(
        data=data.model_dump(),
        message=_('users.create'),
        status_code=201
    )



