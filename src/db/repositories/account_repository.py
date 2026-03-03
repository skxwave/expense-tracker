from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Account as AccountORM
from src.db.models import Transaction as TransactionORM
from src.models.domain.account import Account as AccountDomain
from .base import BaseRepository


class AccountRepository(BaseRepository[AccountDomain, AccountORM]):
    """Repository for Account model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize account repository with session."""
        super().__init__(session, AccountDomain, AccountORM)

    async def create(self, domain_obj: AccountDomain) -> AccountDomain:
        db_data = domain_obj.model_dump(exclude={"id"})
        db_obj = self.db_model(**db_data)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj, with_for_update=False)

        db_obj = await self.session.scalar(
            select(self.db_model)
            .where(self.db_model.id == db_obj.id)
            .options(selectinload(AccountORM.transactions))
        )

        return self._to_domain(db_obj)

    async def get_account(
        self,
        account_id: int,
        user_id: int,
    ) -> AccountDomain:
        account = await self.session.scalar(
            select(self.db_model).where(
                self.db_model.id == account_id,
                self.db_model.user_id == user_id,
            )
        )

        if not account:
            return None

        transactions = await self.session.scalars(
            select(TransactionORM)
            .where(TransactionORM.account_id == account_id)
            .order_by(TransactionORM.created_at.desc())
            .limit(5)
        )

        return self.domain_model(
            **account.__dict__,
            transactions=transactions.all(),
        )

    async def get_accounts(
        self,
        user_id: int,
    ) -> list[AccountDomain]:
        subq = select(
            TransactionORM.id,
            func.row_number()
            .over(
                partition_by=TransactionORM.account_id,
                order_by=TransactionORM.created_at.desc(),
            )
            .label("rn"),
        ).subquery()

        stmt = (
            select(AccountORM)
            .where(AccountORM.user_id == user_id)
            .options(
                selectinload(
                    AccountORM.transactions.and_(
                        TransactionORM.id == subq.c.id,
                        subq.c.rn <= 5,
                    )
                )
            )
        )

        result = await self.session.scalars(stmt)
        return [self._to_domain(a) for a in result.unique().all()]
