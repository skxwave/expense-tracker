from typing import AsyncIterable

from dishka import Container, Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

from src.core import settings
from src.db.repositories import UserRepository
from src.db.repositories.transaction_repository import TransactionRepository
from src.services import UserService
from src.services.auth_service import AuthService
from src.services.transaction_service import TransactionService


class DatabaseProvider(Provider):
    """Provides database-related dependencies."""

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            settings.db_url,
            echo=True,
        )

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker
    ) -> AsyncIterable[AsyncSession]:
        async with factory() as session:
            yield session


class RepositoryProvider(Provider):
    """Provides repository dependencies."""

    @provide(scope=Scope.REQUEST)
    async def get_user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    async def get_transaction_repository(
        self, session: AsyncSession
    ) -> TransactionRepository:
        return TransactionRepository(session)


class ServiceProvider(Provider):
    """Provides service dependencies."""

    @provide(scope=Scope.REQUEST)
    async def get_user_service(self, user_repository: UserRepository) -> UserService:
        return UserService(user_repository)

    @provide(scope=Scope.REQUEST)
    async def get_transaction_service(
        self, transaction_repository: TransactionRepository
    ) -> TransactionService:
        return TransactionService(transaction_repository)

    @provide(scope=Scope.REQUEST)
    async def get_auth_service(
        self, user_service: UserService
    ) -> AuthService:
        return AuthService(user_service)


def create_container() -> Container:
    """Create and configure the DI container."""
    return make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )
