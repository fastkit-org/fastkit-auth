from fastkit_core.validation import BaseSchema

class LoginRequest(BaseSchema):
    username: str
    password: str