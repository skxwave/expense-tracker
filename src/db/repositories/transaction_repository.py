from decimal import Decimal
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.transaction import Transaction as TransactionORM, TransactionType
from src.models.domain.transaction import (
    Transaction as TransactionDomain,
)
from .base import BaseRepository


class TransactionRepository(BaseRepository[TransactionDomain, TransactionORM]):
    """
    Repository for Transaction model operations.

    Provides transaction-specific queries for expenses and incomes.
    """

    def __init__(self, session: AsyncSession):
        """Initialize transaction repository with session."""
        super().__init__(session, TransactionDomain, TransactionORM)

    async def get_transactions(
        self,
        user_id: int,
        transaction_type: TransactionType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TransactionDomain]:
        query = (
            select(self.db_model)
            .where(self.db_model.user_id == user_id)
            .order_by(self.db_model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if transaction_type is not None:
            query = query.where(self.db_model.type == transaction_type)

        obj_list = await self.session.scalars(query)
        return [self._to_domain(t) for t in obj_list.all()]

    async def get_transaction_by_user(
        self,
        transaction_id: int,
        user_id: int,
        transaction_type: TransactionType | None = None,
    ) -> TransactionDomain | None:
        query = select(self.db_model).where(
            self.db_model.id == transaction_id,
            self.db_model.user_id == user_id,
        )
        if transaction_type is not None:
            query = query.where(self.db_model.type == transaction_type)

        return self._to_domain(await self.session.scalar(query))
    
    async def get_incomes_and_expenses(
        self,
        user_id: int,
        days: int = 30,
    ) -> tuple[Decimal, Decimal]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(
                    case((self.db_model.type == TransactionType.INCOME, self.db_model.amount), else_=0)
                ), 0).label("total_incomes"),
                func.coalesce(func.sum(
                    case((self.db_model.type == TransactionType.EXPENSE, self.db_model.amount), else_=0)
                ), 0).label("total_expenses"),
            ).where(
                self.db_model.user_id == user_id,
                self.db_model.created_at >= since,
            )
        )
        summary = result.one()
        return summary.total_incomes, summary.total_expenses

        