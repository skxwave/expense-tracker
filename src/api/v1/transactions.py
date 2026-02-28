from fastapi import APIRouter, Depends, status

from src.core.helpers import get_current_user
from src.core.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from src.services import TransactionService, get_transaction_service
from src.db.models import User, TransactionType

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.get("/", response_model=list[TransactionRead])
async def read_transactions(
    transaction_type: TransactionType = TransactionType.EXPENSE,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.get_transactions(
        user_id=current_user.id,
        transaction_type=transaction_type,
    )


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.add_transaction(
        transaction_data=transaction_data,
        user_id=current_user.id,
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
async def read_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.get_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
    )


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.update_transaction(
        transaction_id=transaction_id,
        transaction_data=transaction_data,
        user_id=current_user.id,
    )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.delete_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
