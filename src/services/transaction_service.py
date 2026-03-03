from src.core.exceptions import EntityNotFoundError

from .base_service import BaseService
from src.core.schemas.transaction import TransactionCreate, TransactionUpdate
from src.models.domain.transaction import Transaction as TransactionDomain
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
        if not await self.account_repo.get_account(
            transaction_data.account_id, user_id
        ):
            raise EntityNotFoundError(
                f"Account with id {transaction_data.account_id} not found"
            )

        new_transaction = TransactionDomain(
            **transaction_data.model_dump(),
            user_id=user_id,
        )
        return await self.repo.create(new_transaction)

    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data: TransactionUpdate,
        user_id: int,
    ) -> TransactionDomain:
        if not await self.repo.get_transaction_by_user(transaction_id, user_id):
            raise EntityNotFoundError(f"Transaction with id {transaction_id} not found")

        update_dict = transaction_data.model_dump(exclude_unset=True)
        update_dict["user_id"] = user_id
        return await self.repo.update(transaction_id, update_dict)

    async def delete_transaction(
        self,
        transaction_id: int,
        user_id: int,
    ) -> None:
        if not await self.repo.get_transaction_by_user(transaction_id, user_id):
            raise EntityNotFoundError(f"Transaction with id {transaction_id} not found")
        await self.repo.delete(transaction_id)
