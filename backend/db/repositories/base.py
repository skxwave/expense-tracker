from abc import ABC
from typing import Generic, TypeVar, Type, Any, Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Abstract base repository implementing common CRUD operations.
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        """
        Initialize repository with database session and model.

        Args:
            session: SQLAlchemy async session
            model: SQLAlchemy model class
        """
        self._session = session
        self._model = model

    @property
    def session(self) -> AsyncSession:
        """Get the database session."""
        return self._session

    @property
    def model(self) -> Type[ModelType]:
        """Get the model class."""
        return self._model

    async def get_by_id(self, id: int) -> ModelType | None:
        """
        Get a single record by ID.

        Args:
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        return await self._session.get(self._model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
    ) -> Sequence[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column name to order by

        Returns:
            List of model instances
        """
        query = select(self._model).offset(skip).limit(limit)

        if order_by:
            query = query.order_by(order_by)

        result = await self._session.scalars(query)
        return result.all()

    async def get_by_field(
        self,
        field: str,
        value: Any,
        single: bool = False,
    ) -> ModelType | Sequence[ModelType] | None:
        """
        Get records by a specific field value.

        Args:
            field: Field name to filter by
            value: Value to match
            single: If True, return single result; otherwise return all matches

        Returns:
            Single model instance, list of instances, or None
        """
        query = select(self._model).where(getattr(self._model, field) == value)

        if single:
            result = await self._session.scalar(query)
            return result

        result = await self._session.scalars(query)
        return result.all()

    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record.

        Args:
            **kwargs: Field values for the new record

        Returns:
            Created model instance
        """
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.commit()
        await self._session.refresh(instance)
        return instance

    async def create_many(self, records: list[dict[str, Any]]) -> Sequence[ModelType]:
        """
        Create multiple records in bulk.

        Args:
            records: List of dictionaries containing field values

        Returns:
            List of created model instances
        """
        instances = [self._model(**record) for record in records]
        self._session.add_all(instances)
        await self._session.commit()

        # Refresh all instances
        for instance in instances:
            await self._session.refresh(instance)

        return instances

    async def update_by_id(self, id: int, **kwargs) -> ModelType | None:
        """
        Update a record by ID.

        Args:
            id: Record ID
            **kwargs: Fields to update

        Returns:
            Updated model instance or None if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self._session.commit()
        await self._session.refresh(instance)
        return instance

    async def update_many(self, filters: dict[str, Any], **kwargs) -> int:
        """
        Update multiple records matching filters.

        Args:
            filters: Dictionary of field:value pairs to filter records
            **kwargs: Fields to update

        Returns:
            Number of records updated
        """
        stmt = update(self._model)

        for field, value in filters.items():
            stmt = stmt.where(getattr(self._model, field) == value)

        stmt = stmt.values(**kwargs)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount

    async def delete_by_id(self, id: int) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self._session.delete(instance)
        await self._session.commit()
        return True

    async def delete_many(self, filters: dict[str, Any]) -> int:
        """
        Delete multiple records matching filters.

        Args:
            filters: Dictionary of field:value pairs to filter records

        Returns:
            Number of records deleted
        """
        stmt = delete(self._model)

        for field, value in filters.items():
            stmt = stmt.where(getattr(self._model, field) == value)

        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount

    async def exists(self, **kwargs) -> bool:
        """
        Check if a record exists with given conditions.

        Args:
            **kwargs: Field:value pairs to check

        Returns:
            True if exists, False otherwise
        """
        query = select(self._model)

        for field, value in kwargs.items():
            query = query.where(getattr(self._model, field) == value)

        query = select(func.count()).select_from(query.subquery())
        result = await self._session.scalar(query)
        return result > 0

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """
        Count records matching optional filters.

        Args:
            filters: Optional dictionary of field:value pairs to filter records

        Returns:
            Number of records
        """
        query = select(func.count()).select_from(self._model)

        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self._model, field) == value)

        result = await self._session.scalar(query)
        return result or 0
