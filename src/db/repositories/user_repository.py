from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations.

    Provides user-specific queries beyond basic CRUD.
    """

    def __init__(self, session: AsyncSession):
        """Initialize user repository with session."""
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_by_field("username", username, single=True)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_by_field("email", email, single=True)

    async def activate_user(self, user_id: int) -> User | None:
        return await self.update_by_id(user_id, is_active=True)

    async def deactivate_user(self, user_id: int) -> User | None:
        return await self.update_by_id(user_id, is_active=False)

    async def verify_user(self, user_id: int) -> User | None:
        return await self.update_by_id(user_id, is_verified=True)

    async def update_password(self, user_id: int, hashed_password: str) -> User | None:
        return await self.update_by_id(user_id, hashed_password=hashed_password)
