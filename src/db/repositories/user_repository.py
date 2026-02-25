from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User as UserORM
from src.models.domain.user import User as UserDomain
from .base import BaseRepository


class UserRepository(BaseRepository[UserDomain, UserORM]):
    """
    Repository for User model operations.

    Provides user-specific queries beyond basic CRUD.
    """

    def __init__(self, session: AsyncSession):
        """Initialize user repository with session."""
        super().__init__(session, UserDomain, UserORM)

    async def activate_user(self, user_id: int) -> UserDomain | None:
        return await self.update(user_id, {"is_active": True})

    async def deactivate_user(self, user_id: int) -> UserDomain | None:
        return await self.update(user_id, {"is_active": False})

    async def verify_user(self, user_id: int) -> UserDomain | None:
        return await self.update(user_id, {"is_verified": True})

    async def update_password(self, user_id: int, hashed_password: str) -> UserDomain | None:
        return await self.update(user_id, {"hashed_password": hashed_password})

    async def get_by_username(self, username: str) -> UserDomain | None:
        obj = await self.session.scalar(
            select(UserORM).where(UserORM.username == username),
        )
        return self._to_domain(obj)

    async def get_by_email(self, email: str) -> UserDomain | None:
        obj = await self.session.scalar(
            select(UserORM).where(UserORM.email == email),
        )
        return self._to_domain(obj)
