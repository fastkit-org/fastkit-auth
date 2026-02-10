from passlib.context import CryptContext
from fastkit_core.config import config
from typing import Optional, Dict
from datetime import datetime, timedelta, timezone
import jwt

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

class JwtHelper:

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = (datetime.now(timezone.utc) +
                  (expires_delta or timedelta(seconds=config('auth.JWT_LIFETIME_SECONDS'))))

        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, config('auth.JWT_TOKEN_SECRET'), algorithm=config('auth.JWT_ALGORITHM'))

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = (datetime.now(timezone.utc) +
                  (expires_delta or timedelta(seconds=config('auth.JWT_REFRESH_LIFETIME_SECONDS'))))

        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, config('auth.JWT_REFRESH_SECRET_KEY'), algorithm=config('auth.JWT_ALGORITHM'))

    @staticmethod
    def verify_token(token: str, refresh: bool = False) -> Optional[Dict]:
        secret = config('auth.JWT_REFRESH_SECRET_KEY') if refresh else config('auth.JWT_TOKEN_SECRET')
        return jwt.decode(token, secret, algorithm=config('auth.JWT_ALGORITHM'))

    @classmethod
    def refresh_access_token(cls, token: str) -> Optional[Dict]:
        payload = cls.verify_token(token, refresh=True)

        if not payload or payload.get('type') != "refresh":
            return None

        user_data = {"sub": payload.get("sub"), "role": payload.get("role")}
        new_access = cls.create_access_token(user_data)
        return {
            "access_token": new_access,
            "token_type": "bearer"
        }
