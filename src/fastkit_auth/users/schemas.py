from fastapi_users import schemas
from fastkit_core.validation import PasswordValidatorMixin

class UserCreate(schemas.BaseUserCreate, PasswordValidatorMixin):
    first_name: str
    last_name: str