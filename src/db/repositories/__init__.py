from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import db_session_manager
from .base import BaseRepository
from .user_repository import UserRepository
from .transaction_repository import TransactionRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "TransactionRepository",
]


def get_user_repository(
    session: AsyncSession = Depends(db_session_manager.get_async_session),
) -> UserRepository:
    """Factory function to get UserRepository instance."""
    return UserRepository(session)


def get_transaction_repository(
    session: AsyncSession = Depends(db_session_manager.get_async_session),
) -> TransactionRepository:
    """Factory function to get TransactionRepository instance."""
    return TransactionRepository(session)
