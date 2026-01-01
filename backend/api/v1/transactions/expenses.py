from fastapi import APIRouter, Depends

from core.helpers import get_current_user
from db.repositories import TransactionRepository, get_transaction_repository
from db.models import User, TransactionType

router = APIRouter(
    prefix="/transactions/expenses",
    tags=["transactions"],
)


@router.get("/")
async def read_expenses(
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    return await transaction_repository.get_expenses(user_id=current_user.id)


@router.post("/")
async def create_expense(
    amount: float,
    description: str | None = "",
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    return await transaction_repository.create(
        user_id=current_user.id,
        amount=amount,
        description=description,
        type=TransactionType.EXPENSE,
    )


@router.get("/{expense_id}")
async def read_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    transaction = await transaction_repository.get_by_id_type_and_user(
        user_id=current_user.id,
        transaction_id=expense_id,
        transaction_type=TransactionType.EXPENSE,
    )
    return transaction if transaction else {"detail": "Expense not found"}


@router.put("/{expense_id}")
async def update_expense(
    expense_id: int,
    current_user=Depends(get_current_user),
):
    return {"message": f"Expense {expense_id} updated"}


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user=Depends(get_current_user),
):
    return {"message": f"Expense {expense_id} deleted"}
