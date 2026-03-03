from src.core.exceptions import EntityNotFoundError, EntityAlreadyExistsError, DomainException
from src.core.schemas.account import AccountCreate

from .base_service import BaseService
from src.models.domain.account import Account as AccountDomain
from src.db.repositories import AccountRepository
from sqlalchemy.exc import IntegrityError


class AccountService(BaseService):
    def __init__(
        self,
        account_repository: AccountRepository,
    ):
        self.repo = account_repository

    async def get_account(
        self,
        account_id: int,
        user_id: int,
    ) -> AccountDomain:
        obj = await self.repo.get_account(account_id, user_id)
        if not obj:
            raise EntityNotFoundError(f"Account with id {account_id} not found")
        return obj

    async def get_accounts(
        self,
        user_id: int,
    ) -> AccountDomain:
        return await self.repo.get_accounts(user_id)
    
    async def create(
        self,
        data: AccountCreate,
        user_id: int,
    ) -> AccountDomain:
        new_account = AccountDomain(
            **data.model_dump(),
            user_id=user_id,
        )
        try:
            return await self.repo.create(new_account)
        except IntegrityError as e:
            constraint_name = getattr(e.orig, 'constraint_name', None) or str(e.orig)
        
            if "uq_user_account_number" in constraint_name:
                raise EntityAlreadyExistsError("An account with this number already exists.")
            
            raise DomainException("Something went wrong...")
