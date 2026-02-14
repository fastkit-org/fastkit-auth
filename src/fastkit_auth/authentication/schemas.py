from fastkit_core.validation import BaseSchema, PasswordValidatorMixin
from pydantic import  EmailStr, model_validator
from fastkit_core.i18n import _

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str

class RessetPasswordRequest(BaseSchema):
    email: EmailStr

class UpdatePassword(BaseSchema, PasswordValidatorMixin):
    code: str
    password: str
    password_confirmation: str

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirmation:
            raise ValueError(_('validation.password.password_is_not_confirmed'))
        return self
