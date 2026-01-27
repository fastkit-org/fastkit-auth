from fastkit_auth.users.auth import get_user_manager, auth_backend, UserManager
from fastkit_auth.authentication.schemas import LoginRequest
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from fastkit_core.i18n import _
from fastapi.security import OAuth2PasswordRequestForm
from fastkit_core.http import success_response, error_response


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/login', name='auth.login')
async def login(login_data: LoginRequest, user_manager: UserManager = Depends(get_user_manager)) -> JSONResponse:
    """Custom login sa email"""
    user = await user_manager.authenticate(
        credentials = OAuth2PasswordRequestForm(
            username=login_data.email.__str__(),
            password=login_data.password
        )

    )

    if not user:
        return error_response(message=_('auth.invalid_credentials'))

    token = await auth_backend.get_strategy().write_token(user)

    return success_response(
        data={
            "access_token": token,
            "token_type": "bearer"
        }
    )
