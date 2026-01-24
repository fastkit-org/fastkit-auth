from fastapi import FastAPI
from fastkit_auth.authentication.router import router as authentication_router


app = FastAPI()

app.include_router(authentication_router)
