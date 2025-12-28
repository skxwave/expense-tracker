from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth_config import get_current_user
from db import db_session_manager
from db.models import Transaction, User, TransactionType

router = APIRouter(
    prefix="/transactions/expenses",
    tags=["transactions"],
)


@router.get("/")
async def read_expenses(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_manager.get_async_session),
):
    async with session as session:
        expenses = await session.scalars(
            select(Transaction).where(
                Transaction.user_id == current_user.id,
                Transaction.type == TransactionType.EXPENSE,
            )
        )
    return {
        "data": expenses.all(),
    }


@router.post("/")
async def create_expense(
    amount: float,
    description: str | None = "",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_manager.get_async_session),
):
    async with session as session:
        expense = Transaction(
            user_id=current_user.id,
            amount=amount,
            description=description,
            type=TransactionType.EXPENSE,
        )
        session.add(expense)
        await session.commit()

    return {
        "expense": expense,
    }


@router.get("/{expense_id}")
async def read_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_session_manager.get_async_session),
):
    async with session as session:
        expense = await session.scalar(
            select(Transaction).where(
                Transaction.user_id == current_user.id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.id == expense_id,
            )
        )
        if not expense:
            return {
                "error": "Expense not found",
            }
        
    return {
        "data": expense,
    }


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
