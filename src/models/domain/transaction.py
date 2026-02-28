from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import TransactionType


class Transaction(BaseModel):
    id: int | None = None
    amount: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    description: str
    type: TransactionType
    account_id: int | None = None
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
