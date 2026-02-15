from fastapi import APIRouter, Depends

from core.helpers import get_current_user
from db.repositories import TransactionRepository, get_transaction_repository
from db.models import User, TransactionType

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.get("/total")
async def get_incomes_and_expenses_total(
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    expenses = await transaction_repository.get_total_by_type(
        user_id=current_user.id,
        transaction_type=TransactionType.EXPENSE,
    )
    incomes = await transaction_repository.get_total_by_type(
        user_id=current_user.id,
        transaction_type=TransactionType.INCOME,
    )
    return {
        "total_expenses": expenses,
        "total_incomes": incomes,
    }
