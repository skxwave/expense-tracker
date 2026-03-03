from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Account as AccountORM
from src.models.domain.account import Account as AccountDomain
from .base import BaseRepository


class AccountRepository(BaseRepository[AccountDomain, AccountORM]):
    """Repository for Account model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize account repository with session."""
        super().__init__(session, AccountDomain, AccountORM)
