from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from core import settings
from .models import User


#TODO: Make it better
class AsyncSessionManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.sessionmaker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency that yields a database session and closes it after the request.
        """
        async with self.sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


db_session_manager = AsyncSessionManager(database_url=settings.db_url)


async def get_user_db(
    session: AsyncSession = Depends(db_session_manager.get_async_session)
):
    yield SQLAlchemyUserDatabase(session, User)
