from decimal import Decimal

from src.core.exceptions import EntityNotFoundError, InsufficientFundsError

from .base_service import BaseService
from src.core.schemas.transaction import TransactionCreate, TransactionUpdate
from src.models.domain.transaction import (
    Transaction as TransactionDomain,
    TransactionSummary as TransactionSummaryDomain,
)
from src.db.repositories import TransactionRepository, AccountRepository
from src.models.enums import TransactionType


class TransactionService(BaseService):
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        account_repository: AccountRepository,
    ):
        self.repo = transaction_repository
        self.account_repo = account_repository

    async def get(self, id: int) -> TransactionDomain:
        return self._require(
            await self.repo.get(id),
            f"Transaction with id {id} not found",
        )

    async def get_transaction(
        self,
        transaction_id: int,
        user_id: int,
    ) -> TransactionDomain:
        return self._require(
            await self.repo.get_transaction_by_user(transaction_id, user_id),
            f"Transaction with id {transaction_id} not found",
        )

    async def get_transactions(
        self,
        user_id: int,
        transaction_type: TransactionType,
    ) -> list[TransactionDomain]:
        return await self.repo.get_transactions(
            user_id=user_id,
            transaction_type=transaction_type,
        )

    async def add_transaction(
        self,
        transaction_data: TransactionCreate,
        user_id: int,
    ) -> TransactionDomain:
        balance = await self.account_repo.get_balance(transaction_data.account_id, user_id)
        if balance is None:
            raise EntityNotFoundError(f"Account with id {transaction_data.account_id} not found")

        if transaction_data.type == TransactionType.EXPENSE and balance < transaction_data.amount:
            raise InsufficientFundsError(
                f"Insufficient funds: balance {balance}, required {transaction_data.amount}"
            )

        result = await self.repo.create(
            TransactionDomain(**transaction_data.model_dump(), user_id=user_id)
        )
        delta = -transaction_data.amount if transaction_data.type == TransactionType.EXPENSE else transaction_data.amount
        await self.account_repo.adjust_balance(transaction_data.account_id, delta)
        return result

    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data: TransactionUpdate,
        user_id: int,
    ) -> TransactionDomain:
        old = await self.repo.get_transaction_by_user(transaction_id, user_id)
        if not old:
            raise EntityNotFoundError(f"Transaction with id {transaction_id} not found")

        # Delta that reverses the old transaction's effect on its account
        old_reverse: Decimal = old.amount if old.type == TransactionType.EXPENSE else -old.amount

        if old.account_id != transaction_data.account_id:
            # Account changed: verify new account ownership and check funds
            new_balance = await self.account_repo.get_balance(transaction_data.account_id, user_id)
            if new_balance is None:
                raise EntityNotFoundError(f"Account with id {transaction_data.account_id} not found")

            if transaction_data.type == TransactionType.EXPENSE and new_balance < transaction_data.amount:
                raise InsufficientFundsError(
                    f"Insufficient funds: balance {new_balance}, required {transaction_data.amount}"
                )

            await self.account_repo.adjust_balance(old.account_id, old_reverse)
            new_delta = -transaction_data.amount if transaction_data.type == TransactionType.EXPENSE else transaction_data.amount
            await self.account_repo.adjust_balance(transaction_data.account_id, new_delta)
        else:
            # Same account: check balance after reverting old effect
            current_balance = await self.account_repo.get_balance(old.account_id, user_id)
            reverted_balance = current_balance + old_reverse

            if transaction_data.type == TransactionType.EXPENSE and reverted_balance < transaction_data.amount:
                raise InsufficientFundsError(
                    f"Insufficient funds: balance {reverted_balance}, required {transaction_data.amount}"
                )

            new_delta = -transaction_data.amount if transaction_data.type == TransactionType.EXPENSE else transaction_data.amount
            await self.account_repo.adjust_balance(old.account_id, old_reverse + new_delta)

        update_dict = transaction_data.model_dump(exclude_unset=True)
        update_dict["user_id"] = user_id
        return await self.repo.update(transaction_id, update_dict)

    async def delete_transaction(
        self,
        transaction_id: int,
        user_id: int,
    ) -> None:
        old = await self.repo.get_transaction_by_user(transaction_id, user_id)
        if not old:
            raise EntityNotFoundError(f"Transaction with id {transaction_id} not found")

        reverse: Decimal = old.amount if old.type == TransactionType.EXPENSE else -old.amount
        await self.repo.delete(transaction_id)
        await self.account_repo.adjust_balance(old.account_id, reverse)

    async def get_summary(
        self,
        user_id: int,
    ) -> TransactionSummaryDomain:
        incomes, expenses = await self.repo.get_incomes_and_expenses(user_id)
        balance = await self.account_repo.get_overall_balance(user_id)
        return TransactionSummaryDomain(
            total_balance=balance,
            total_incomes=incomes,
            total_expenses=expenses,
        )
