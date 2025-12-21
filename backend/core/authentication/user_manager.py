import uuid

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, UUIDIDMixin, exceptions
from sqlalchemy import or_, select

from core import settings
from db import get_user_db, db_session_manager
from db.models import User


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.reset_password_token_secret
    reset_password_token_lifetime_seconds = 3600
    verification_token_secret = settings.verification_token_secret
    verification_token_lifetime_seconds = 3600

    # async def authenticate(
    #     self, credentials: OAuth2PasswordRequestForm
    # ):
    #     """
    #     Authenticate and return a user following an email or username and a password.

    #     Will automatically upgrade password hash if necessary.

    #     :param credentials: The user credentials.
    #     :return: The authenticated user of type models.UP if credentials are valid,
    #     otherwise None.
    #     """
    #     try:
    #         async with db_session_manager.get_async_session() as session:
    #             # Check both email and username fields
    #             query = select(User).where(
    #                 or_(
    #                     User.email == credentials.username,
    #                     User.username == credentials.username,
    #                 )
    #             )
    #             result = await session.execute(query)
    #             user: User | None = result.scalar_one_or_none()
                
    #         # If user not found, hash password to mitigate timing attacks
    #         if user is None:
    #             self.password_helper.hash(credentials.password)
    #             return None
                
    #     except Exception:
    #         # Run password hasher to mitigate timing attacks
    #         self.password_helper.hash(credentials.password)
    #         return None

    #     verified, updated_password_hash = self.password_helper.verify_and_update(
    #         credentials.password, user.hashed_password
    #     )
    #     if not verified:
    #         return None
    #     # Update password hash to a more robust one if needed
    #     if updated_password_hash is not None:
    #         await self.user_db.update(user, {"hashed_password": updated_password_hash})

    #     return user

    async def on_after_register(
        self,
        user: User,
        request: Request | None = None,
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Request | None = None,
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
