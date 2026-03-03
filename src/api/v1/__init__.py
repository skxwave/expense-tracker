from fastapi import APIRouter

from .users import router as user_router
from .transactions import router as transactions_router
from .accounts import router as accounts_router

__all__ = [
    "user_router",
    "transactions_router",
    "accounts_router",
]

router = APIRouter(prefix="/api/v1")
router.include_router(user_router)
router.include_router(transactions_router)
router.include_router(accounts_router)
