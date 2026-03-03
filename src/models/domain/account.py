from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .transaction import Transaction
from src.models.enums import AccountType


class Account(BaseModel):
    id: int | None = None
    name: str | None = None
    number: int | None = None
    holder: str | None = None
    value: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    description: str | None = None
    type: AccountType | None = None
    transactions: list[Transaction] | None = None
    user_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
