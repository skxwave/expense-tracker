from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.transaction import Transaction, TransactionType
from .base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """
    Repository for Transaction model operations.

    Provides transaction-specific queries for expenses and incomes.
    """

    def __init__(self, session: AsyncSession):
        """Initialize transaction repository with session."""
        super().__init__(session, Transaction)

    async def get_transactions_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Transaction]:
        query = (
            select(self._model)
            .where(self._model.user_id == user_id)
            .order_by(self._model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.scalars(query)
        return result.all()

    async def get_transactions_by_user_and_type(
        self,
        user_id: int,
        transaction_type: TransactionType,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Transaction]:
        query = (
            select(self._model)
            .where(self._model.user_id == user_id, self._model.type == transaction_type)
            .order_by(self._model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.scalars(query)
        return result.all()

    async def get_transaction_by_id_type_and_user(
        self,
        transaction_id: int,
        user_id: int,
        transaction_type: TransactionType,
    ) -> Transaction | None:
        query = select(self._model).where(
            self._model.id == transaction_id,
            self._model.user_id == user_id,
            self._model.type == transaction_type,
        )

        result = await self._session.scalar(query)
        return result

    async def get_transactions_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        transaction_type: TransactionType | None = None,
    ) -> Sequence[Transaction]:
        query = select(self._model).where(
            self._model.user_id == user_id,
            self._model.created_at >= start_date,
            self._model.created_at <= end_date,
        )

        if transaction_type:
            query = query.where(self._model.type == transaction_type)

        query = query.order_by(self._model.created_at.desc())

        result = await self._session.scalars(query)
        return result.all()

    async def get_total_by_type(
        self,
        user_id: int,
        transaction_type: TransactionType,
    ) -> Decimal:
        query = select(func.sum(self._model.amount)).where(
            self._model.user_id == user_id, self._model.type == transaction_type
        )

        result = await self._session.scalar(query)
        return result or Decimal(0)

    async def get_total_expenses(self, user_id: int) -> Decimal:
        return await self.get_total_by_type(user_id, TransactionType.EXPENSE)

    async def get_total_incomes(self, user_id: int) -> Decimal:
        return await self.get_total_by_type(user_id, TransactionType.INCOME)

    async def get_balance(self, user_id: int) -> Decimal:
        total_income = await self.get_total_incomes(user_id)
        total_expense = await self.get_total_expenses(user_id)
        return total_income - total_expense

    async def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        transaction_type: TransactionType,
        **kwargs,
    ) -> Transaction | None:
        transaction = await self.get_transaction_by_id_type_and_user(
            transaction_id,
            user_id,
            transaction_type=transaction_type,
        )
        if not transaction:
            return None

        return await self.update_by_id(transaction_id, **kwargs)

    async def delete_transaction(
        self,
        transaction_id: int,
        transaction_type: TransactionType,
        user_id: int,
    ) -> bool:
        transaction = await self.get_transaction_by_id_type_and_user(
            transaction_id,
            user_id,
            transaction_type=transaction_type,
        )
        if not transaction:
            return False

        return await self.delete_by_id(transaction_id)
