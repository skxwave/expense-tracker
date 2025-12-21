from fastapi import APIRouter

from .users import router as user_router

__all__ = [
    "user_router",
]

router = APIRouter(prefix="/api/v1")
router.include_router(user_router)
