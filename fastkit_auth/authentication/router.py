from fastkit_auth.users.auth import auth_backend, fastapi_users
from fastapi import APIRouter

router = APIRouter(prefix='auth', tags=['Auth'])


# JWT login
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)