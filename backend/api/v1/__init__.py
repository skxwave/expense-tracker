from fastapi import APIRouter

from .users import router as user_router
from .transactions.incomes import router as incomes_router
from .transactions.expenses import router as expenses_router

__all__ = [
    "user_router",
    "incomes_router",
    "expenses_router",
]

router = APIRouter(prefix="/api/v1")
router.include_router(user_router)
router.include_router(incomes_router)
router.include_router(expenses_router)
