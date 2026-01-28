from fastapi import FastAPI
from fastkit_auth.authentication.router import router as authentication_router
from fastkit_auth.users.router import registration_router
from fastkit_core.database import init_async_database
from fastkit_core.config import ConfigManager
configuration = ConfigManager(modules=['app', 'database', 'auth'])
init_async_database(configuration)

app = FastAPI()

app.include_router(authentication_router)
app.include_router(registration_router)
