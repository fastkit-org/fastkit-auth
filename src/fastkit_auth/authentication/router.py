from fastkit_auth.authentication.schemas import LoginRequest, ResetPasswordRequest, UpdatePassword
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from fastkit_core.i18n import _
from fastkit_core.http import success_response, error_response
from fastkit_auth.authentication.service import AuthService
from fastkit_core.validation.errors import format_validation_errors
from fastkit_core.database import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError


router = APIRouter(prefix='/auth', tags=['Auth'])

def get_service(session: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(session)

@router.post('/login', name='auth.login', response_model=None)
async def login(data: LoginRequest, service: AuthService = Depends(get_service)) -> JSONResponse:
    try:
        response = await service.authenticate(email=data.email, password=data.password)
        return success_response(data=response)
    except ValidationError as e:
        errors = format_validation_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=422
        )

@router.post('/reset-password', name='auth.reset_password')
async def reset_password(data: ResetPasswordRequest, service: AuthService = Depends(get_service)) -> JSONResponse:
    try:
        await service.reset_password(email=data.email.__str__())
        return success_response(message=_('auth.email_sent'))
    except ValidationError as e:
        errors = format_validation_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=422
        )

@router.post('/update-password', name='auth.update_password')
async def update_password(data: UpdatePassword, service: AuthService = Depends(get_service)) -> JSONResponse:
    try:
        await service.update_password(token=data.code.__str__(), password=data.password.__str__())
        return success_response(message=_('auth.password_updated'))
    except ValidationError as e:
        errors = format_validation_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=422
        )