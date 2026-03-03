from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.core.schemas.transaction import TransactionRead
from src.models.enums import AccountType


class AccountBase(BaseModel):
    name: str = Field(
        ...,
        description="Account name",
        examples=["Monobank"],
    )
    number: int = Field(
        ...,
        description="",
        examples=["12345678"],
    )
    holder: str = Field(
        ...,
        description="Holder name",
        examples=["John Doe"],
    )
    value: Decimal = Field(
        ...,
        gt=0,
        description="Account value (must be positive)",
        examples=[2000],
    )
    description: str | None = None
    type: AccountType = Field(
        ...,
        description="Account type",
        examples=["credit", "debit"],
    )


class AccountCreate(AccountBase):
    pass


class AccountRead(BaseModel):
    id: int
    transactions: list[TransactionRead] = []
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
