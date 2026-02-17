from typing import Optional
from pydantic import ConfigDict
from uuid import UUID
from fastkit_core.validation import PasswordValidatorMixin, BaseSchema
from pydantic import EmailStr, field_serializer
from datetime import datetime

class UserCreate(BaseSchema, PasswordValidatorMixin):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserUpdate(BaseSchema):
    first_name: str
    last_name: str
    email: EmailStr
    is_superuser: bool

class UserResponse(BaseSchema):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    email_verified_at: Optional[datetime] | None
    is_active: bool
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('user_id')
    def serialize_uuid(self, v: UUID) -> str:
        return str(v)

    @field_serializer('expires_at')
    def serialize_dt(self, v: datetime) -> str | None:
        return v.isoformat() if v else None