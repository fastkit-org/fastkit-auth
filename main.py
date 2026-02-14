from fastapi import FastAPI
from fastkit_auth.authentication.router import router as authentication_router
from fastkit_auth.users.router import registration_router, profile_router
from fastkit_core.database import init_async_database
from fastkit_core.config import ConfigManager
from fastkit_core.http.exception_handlers import register_exception_handlers

configuration = ConfigManager(modules=['app', 'database', 'auth'])
init_async_database(configuration)

app = FastAPI()
register_exception_handlers(app=app)

app.include_router(authentication_router)
app.include_router(registration_router)
app.include_router(profile_router)
