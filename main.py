from fastapi import FastAPI, Request
from fastkit_auth.authentication.router import router as authentication_router
from fastkit_auth.users.router import registration_router
from fastkit_auth.tokens.router import token_router
from fastkit_core.database import init_async_database
from fastkit_core.config import ConfigManager
from fastkit_core.validation import BaseSchema
from fastapi.exceptions import RequestValidationError
from fastkit_core.http import error_response
from fastkit_core.i18n import _
from pydantic import ValidationError

configuration = ConfigManager(modules=['app', 'database', 'auth'])
init_async_database(configuration)

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    validation_error = ValidationError.from_exception_data(
        title=exc.__class__.__name__,
        line_errors=exc.errors()
    )

    return error_response(
        message=_('validation.failed'),
        errors= BaseSchema.format_errors(validation_error),
        status_code=422
    )

app.include_router(authentication_router)
app.include_router(registration_router)
app.include_router(token_router)
