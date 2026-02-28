from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.transaction import Transaction as TransactionORM, TransactionType
from src.models.domain.transaction import Transaction as TransactionDomain
from .base import BaseRepository


class TransactionRepository(BaseRepository[TransactionDomain, TransactionORM]):
    """
    Repository for Transaction model operations.

    Provides transaction-specific queries for expenses and incomes.
    """

    def __init__(self, session: AsyncSession):
        """Initialize transaction repository with session."""
        super().__init__(session, TransactionDomain, TransactionORM)

    async def get_transactions_by_user_id(
        self,
        user_id: int,
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

        obj_list = await self.session.scalars(query)
        return [self._to_domain(t) for t in obj_list.all()]

    async def get_transactions_by_user_and_type(
        self,
        user_id: int,
        transaction_type: TransactionType,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TransactionDomain]:
        query = (
            select(self.db_model)
            .where(
                self.db_model.user_id == user_id, self.db_model.type == transaction_type
            )
            .order_by(self.db_model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        obj_list = await self.session.scalars(query)
        return [self._to_domain(t) for t in obj_list.all()]

    async def get_transaction_by_id_type_and_user(
        self,
        transaction_id: int,
        user_id: int,
        transaction_type: TransactionType,
    ) -> TransactionDomain | None:
        query = select(self.db_model).where(
            self.db_model.id == transaction_id,
            self.db_model.user_id == user_id,
            self.db_model.type == transaction_type,
        )

        obj = await self.session.scalar(query)

        if not obj:
            return None
        
        return self._to_domain(obj)
    
    async def get_transaction_by_id_and_user(
        self,
        transaction_id: int,
        user_id: int,
    ) -> TransactionDomain | None:
        query = select(self.db_model).where(
            self.db_model.id == transaction_id,
            self.db_model.user_id == user_id,
        )

        obj = await self.session.scalar(query)

        if not obj:
            return None
        
        return self._to_domain(obj)
