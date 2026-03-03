from src.core.exceptions import EntityAlreadyExistsError

from .base_service import BaseService
from src.core.schemas.user import UserCreate
from src.models.domain.user import User as UserDomain
from src.db.repositories import UserRepository
from src.core.auth_config import get_password_hash


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.repo = user_repository

    async def get_by_id(self, id: int) -> UserDomain:
        return self._require(await self.repo.get(id), f"User with id {id} not found")

    async def get_by_email(self, email: str) -> UserDomain:
        return self._require(await self.repo.get_by_email(email), f"User with email {email} not found")

    async def get_by_username(self, username: str) -> UserDomain:
        return self._require(await self.repo.get_by_username(username), f"User with username {username} not found")

    async def register_user(self, user_data: UserCreate) -> UserDomain:
        if await self.repo.get_by_email(user_data.email):
            raise EntityAlreadyExistsError(f"User with email {user_data.email} already exists")

        new_user = UserDomain(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
        )
        return await self.repo.create(new_user)

