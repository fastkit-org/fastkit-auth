from typing import Optional
from pydantic import ConfigDict
from uuid import UUID
from fastkit_core.validation import PasswordValidatorMixin, BaseSchema
from pydantic import EmailStr
from datetime import datetime

class UserCreate(BaseSchema, PasswordValidatorMixin):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    is_superuser: bool

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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }
    )