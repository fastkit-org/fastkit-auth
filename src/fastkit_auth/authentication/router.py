from fastkit_auth.authentication.schemas import LoginRequest
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from fastkit_core.i18n import _
from fastkit_core.http import success_response, error_response
from fastkit_auth.authentication.service import AuthService
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
        errors = LoginRequest.format_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=422
        )