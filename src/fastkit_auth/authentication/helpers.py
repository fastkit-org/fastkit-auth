from passlib.context import CryptContext
from fastkit_core.config import config

_pwd_context = CryptContext(
    schemes=config('auth.PASSWORD_ENCRYPTION_SCHEMES', ['bcrypt']),
    deprecated="auto"
)


class PasswordHelper:

    @staticmethod
    def hash(password: str) -> str:
        return _pwd_context.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        return _pwd_context.needs_update(hashed_password)