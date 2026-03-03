from typing import TypeVar

from src.core.exceptions import EntityNotFoundError

T = TypeVar("T")


class BaseService:
    def _require(self, obj: T | None, message: str) -> T:
        """Raise EntityNotFoundError if obj is None, otherwise return it."""
        if obj is None:
            raise EntityNotFoundError(message)
        return obj
