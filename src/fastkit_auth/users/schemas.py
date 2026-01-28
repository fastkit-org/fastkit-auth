from typing import Optional
from pydantic import ConfigDict
from uuid import UUID
from fastapi_users import schemas
from fastkit_core.validation import PasswordValidatorMixin, BaseSchema
from pydantic import EmailStr, field_serializer
from datetime import datetime

class UserCreate(BaseSchema, schemas.BaseUserCreate, PasswordValidatorMixin):
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