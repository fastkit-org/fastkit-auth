from fastkit_core.validation import BaseSchema
from pydantic import EmailStr

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str