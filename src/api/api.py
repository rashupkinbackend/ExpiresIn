from src.api.auth import router as auth_router
from src.api.documents import router as documents_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(auth_router)
router.include_router(documents_router)
