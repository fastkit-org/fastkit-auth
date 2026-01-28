from fastapi_users import schemas
from fastkit_core.validation import PasswordValidatorMixin, BaseSchema
from pydantic import EmailStr, field_serializer
from uuid import UUID
from datetime import datetime

class UserCreate(schemas.BaseUserCreate, PasswordValidatorMixin):
    first_name: str
    last_name: str

class UserUpdate(BaseSchema):
    first_name: str
    last_name: str
    email: EmailStr

class UserResponse(BaseSchema):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    email_verified_at: datetime
    is_active: bool
    is_superuser: bool
    is_verified: bool

    @field_serializer('email_verified_at')
    def serialize_datetime(self, dt: datetime | None, _info):
        if dt is None:
            return None
        return dt.strftime("%m/%d/%Y")