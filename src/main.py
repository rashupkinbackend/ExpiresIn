from fastapi import FastAPI
from src.api.auth import router as auth_router
from src.api.documents import router as documents_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(documents_router)
