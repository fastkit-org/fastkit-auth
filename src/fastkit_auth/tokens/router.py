from fastapi import APIRouter, Depends
from fastkit_core.http import success_response, error_response
from fastkit_core.database import get_async_db
from fastkit_core.i18n import _
from fastkit_core.validation import BaseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from fastkit_auth.tokens.service import TokenService
from starlette.responses import JSONResponse
from pydantic import ValidationError

token_router = APIRouter(
    tags=['Token']
)

def get_service(session: AsyncSession = Depends(get_async_db)) -> TokenService:
    return TokenService(session)

@token_router.get('/email-confirmation/{token}', name='auth.confirm_email')
async def email_confirmation(token: str, service: TokenService = Depends(get_service)) -> JSONResponse:
    try:
        await service.email_confirmation(token)
        return success_response(message=_('users.email_confirmed'))
    except ValidationError as e:
        errors = BaseSchema.format_errors(e)
        return error_response(
            message=_('validation.failed'),
            errors=errors,
            status_code=422
        )
