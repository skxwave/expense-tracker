from decimal import Decimal

from sqlalchemy import select, func, update as sa_update
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
        return await self._load_with_transactions(db_obj.id)

    async def _load_with_transactions(self, account_id: int) -> AccountDomain | None:
        result = await self.session.scalar(
            select(self.db_model)
            .where(self.db_model.id == account_id)
            .options(selectinload(AccountORM.transactions))
        )
        return self._to_domain(result)

    async def update(
        self, id: int, update_data: AccountDomain | dict
    ) -> AccountDomain | None:
        db_obj = await self.session.get(self.db_model, id)
        if not db_obj:
            return None

        update_dict = (
            update_data.model_dump(exclude_unset=True, exclude={"id"})
            if isinstance(update_data, AccountDomain)
            else update_data
        )
        for field, value in update_dict.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        return await self._load_with_transactions(id)

    async def get_account(
        self,
        account_id: int,
        user_id: int,
    ) -> AccountDomain | None:
        subq = (
            select(TransactionORM.id)
            .where(TransactionORM.account_id == account_id)
            .order_by(TransactionORM.created_at.desc())
            .limit(5)
            .subquery()
        )
        result = await self.session.scalar(
            select(self.db_model)
            .where(
                self.db_model.id == account_id,
                self.db_model.user_id == user_id,
            )
            .options(
                selectinload(AccountORM.transactions.and_(TransactionORM.id.in_(subq)))
            )
        )
        return self._to_domain(result)

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

    async def get_balance(self, account_id: int, user_id: int) -> Decimal | None:
        """Return the current balance of an account, or None if not found / not owned."""
        return await self.session.scalar(
            select(self.db_model.value).where(
                self.db_model.id == account_id,
                self.db_model.user_id == user_id,
            )
        )

    async def adjust_balance(self, account_id: int, delta: Decimal) -> None:
        """Atomically add delta (positive or negative) to the account balance."""
        await self.session.execute(
            sa_update(self.db_model)
            .where(self.db_model.id == account_id)
            .values(value=self.db_model.value + delta)
        )
        await self.session.commit()

    async def get_overall_balance(self, user_id: int) -> Decimal:
        """Return overall balance between all existing accounts"""
        result = await self.session.scalar(
            select(func.sum(self.db_model.value)).where(
                self.db_model.user_id == user_id,
            )
        )
        return result or Decimal(0)
