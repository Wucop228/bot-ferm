from fastapi import FastAPI

from app.api.v1.users import router as users_v1_router
from app.api.v1.auth import router as auth_v1_router

app = FastAPI()

app.include_router(users_v1_router)
app.include_router(auth_v1_router)
