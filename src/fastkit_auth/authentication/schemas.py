from fastkit_core.validation import BaseSchema

class LoginRequest(BaseSchema):
    email: str
    password: str