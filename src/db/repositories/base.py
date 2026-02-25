from abc import ABC
from typing import Generic, TypeVar, Type, Any, Union

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.base import Base


T_Domain = TypeVar("T_Domain")
T_DB = TypeVar("T_DB", bound=Base)


class BaseRepository(ABC, Generic[T_Domain, T_DB]):
    """
    Abstract base repository implementing common CRUD operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        domain_model: Type[T_Domain],
        db_model: Type[T_DB],
    ):
        """
        Initialize repository with database session and model.

        Args:
            session: SQLAlchemy async session
            domain_model: Domain model class
            db_model: SQLAlchemy model class
        """
        self.session = session
        self.domain_model = domain_model
        self.db_model = db_model

    def _to_domain(self, db_obj: Any) -> T_Domain | None:
        if not db_obj:
            return None
        return self.domain_model.model_validate(db_obj)

    async def get(self, id: int) -> T_Domain | None:
        """Get a single record by ID."""
        result = await self.session.get(self.db_model, id)
        return self._to_domain(result)

    async def create(self, domain_obj: T_Domain) -> T_Domain:
        """Create a new record."""
        db_data = domain_obj.model_dump(exclude={"id"})
        db_obj = self.db_model(**db_data)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return self._to_domain(db_obj)

    async def update(
        self,
        id: int,
        update_data: Union[T_Domain, dict[str, Any]],
    ) -> T_Domain | None:
        """Update a record by ID."""
        db_obj = await self.session.get(self.db_model, id)

        if not db_obj:
            return None
        
        if isinstance(update_data, BaseModel):
            update_dict = update_data.model_dump(exclude_unset=True, exclude={"id"})
        else:
            update_dict = update_data

        for field, value in update_dict.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return self._to_domain(db_obj)

    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        db_obj = await self.session.get(self.db_model, id)

        if not db_obj:
            return False

        await self.session.delete(db_obj)
        await self.session.commit()

        return True
