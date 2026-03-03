from src.core.exceptions import EntityNotFoundError
from src.core.schemas.account import AccountCreate

from .base_service import BaseService
from src.models.domain.account import Account as AccountDomain
from src.db.repositories import AccountRepository


class AccountService(BaseService):
    def __init__(
        self,
        account_repository: AccountRepository,
    ):
        self.repo = account_repository

    async def get(
        self,
        id: int,
    ) -> AccountDomain:
        obj = await self.repo.get(id)
        if not obj:
            raise EntityNotFoundError(f"Account with id {id} not found")
        return obj
    
    async def create(
        self,
        data: AccountCreate,
        user_id: int,
    ) -> AccountDomain:
        new_account = AccountDomain(
            **data,
            user_id=user_id,
        )
        return await self.repo.create(new_account)
