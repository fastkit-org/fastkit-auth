from fastapi import Request

from fastapi import APIRouter, Depends, status
from fastkit_core.http import success_response, error_response
from fastkit_core.database import get_async_db
from fastkit_core.i18n import _
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.users.schemas import UserCreate
from fastkit_auth.users.service import UserService
from starlette.responses import JSONResponse
from pydantic import ValidationError
from fastkit_auth.authentication.dependencies import get_current_user
from fastkit_auth.users.models import User

registration_router = APIRouter(
    tags=['Registration']
)

profile_router = APIRouter(
    tags=['Profile']
)

def get_service(session: AsyncSession = Depends(get_async_db)) -> UserService:
    return UserService(session)

@registration_router.post('/registration', name='auth.registration')
async def registration(request: Request, user: UserCreate, service: UserService = Depends(get_service)) -> JSONResponse:
    try:
        service.set_request(request)
        data = await service.create(user.model_dump())
        return success_response(
            data=data.model_dump(mode='json'),
            message=_('users.create'),
            status_code=status.HTTP_201_CREATED
        )
    except ValidationError as e:
        errors = UserCreate.format_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

@registration_router.get('/verify-email/{token}', name='auth.email_verification')
async def verify_email(token: str, service: UserService = Depends(get_service)) -> JSONResponse:
    try:
        await service.email_confirmation(token)
        return success_response(message=_('users.email_confirmed'))
    except ValidationError as e:
        errors = UserCreate.format_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=422
        )

@profile_router.get('/profile', name='auth.profile')
async def profile(current_user: User = Depends(get_current_user)) -> JSONResponse:
    return success_response(data=current_user.model_dump(mode='json'))