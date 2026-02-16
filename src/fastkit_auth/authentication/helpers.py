from passlib.context import CryptContext
from typing import Optional, Dict
from datetime import datetime, timedelta, timezone
import jwt
from fastkit_core.i18n import _
from fastkit_core.config import ConfigManager

configuration = ConfigManager(modules=['auth'])
_pwd_context = CryptContext(
    schemes=configuration.get('auth.PASSWORD_ENCRYPTION_SCHEMES', ['bcrypt']),
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
    def _create_token(data: dict, secret: str, lifetime_seconds: int, token_type: str,
                      expires_delta: Optional[timedelta] = None) -> str:
        if not data.get("sub"):
            raise ValueError(_('auth.token_payload_must_have_sub'))
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(seconds=lifetime_seconds))
        to_encode.update({"exp": expire, "type": token_type, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, secret, algorithm=configuration.get('auth.JWT_ALGORITHM'))

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        return JwtHelper._create_token(
            data,
            secret=configuration.get('auth.JWT_TOKEN_SECRET'),
            lifetime_seconds=configuration.get('auth.JWT_LIFETIME_SECONDS'),
            token_type="access",
            expires_delta=expires_delta
        )

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        return JwtHelper._create_token(
            data,
            secret=configuration.get('auth.JWT_REFRESH_SECRET_KEY'),
            lifetime_seconds=configuration.get('auth.JWT_REFRESH_LIFETIME_SECONDS'),
            token_type="refresh",
            expires_delta=expires_delta
        )

    @staticmethod
    def verify_token(token: str, refresh: bool = False) -> Optional[Dict]:
        try:
            secret = configuration.get('auth.JWT_REFRESH_SECRET_KEY') if refresh else configuration.get('auth.JWT_TOKEN_SECRET')
            return jwt.decode(token, secret, algorithms=[configuration.get('auth.JWT_ALGORITHM')])
        except jwt.ExpiredSignatureError:
            raise ValueError(_('auth.token_expired'))
        except jwt.InvalidTokenError:
            raise ValueError(_('auth.token_invalid'))

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
