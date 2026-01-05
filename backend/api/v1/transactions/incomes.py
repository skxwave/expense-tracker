from fastapi import APIRouter, Depends, HTTPException, status

from core.schemas.transaction import TransactionUpdate, TransactionRead
from core.helpers import get_current_user
from db.repositories import TransactionRepository, get_transaction_repository
from db.models import User, TransactionType

router = APIRouter(
    prefix="/transactions/incomes",
    tags=["transactions"],
)


@router.get("/", response_model=list[TransactionRead])
async def read_incomes(
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    return await transaction_repository.get_transactions_by_user_and_type(
        user_id=current_user.id,
        transaction_type=TransactionType.INCOME,
    )


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_income(
    amount: float,
    description: str | None = "",
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    return await transaction_repository.create(
        user_id=current_user.id,
        amount=amount,
        description=description,
        type=TransactionType.INCOME,
    )


@router.get("/{income_id}", response_model=TransactionRead)
async def read_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    transaction = await transaction_repository.get_transaction_by_id_type_and_user(
        user_id=current_user.id,
        transaction_id=income_id,
        transaction_type=TransactionType.INCOME,
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Income with id {income_id} not found",
        )
    return transaction


@router.put("/{income_id}", response_model=TransactionRead)
async def update_income(
    income_id: int,
    income_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    transaction = await transaction_repository.update_transaction(
        transaction_id=income_id,
        user_id=current_user.id,
        transaction_type=TransactionType.INCOME,
        **income_update.model_dump(exclude_unset=True),
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Income with id {income_id} not found",
        )
    return transaction


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    transaction = await transaction_repository.delete_transaction(
        transaction_id=income_id,
        user_id=current_user.id,
        transaction_type=TransactionType.INCOME,
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Income with id {income_id} not found",
        )
    return None
