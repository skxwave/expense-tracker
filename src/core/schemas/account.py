from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.core.schemas.transaction import TransactionRead
from src.models.enums import AccountType


class AccountBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Account name",
        examples=["Monobank"],
    )
    number: str = Field(
        ...,
        min_length=1,
        max_length=34,
        description="Account number",
        examples=["12345678"],
    )
    holder: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Holder name",
        examples=["John Doe"],
    )
    value: Decimal = Field(
        ...,
        gt=0,
        description="Account value (must be positive)",
        examples=[2000],
    )
    description: str | None = Field(
        None,
        max_length=255,
        description="Optional description",
    )
    type: AccountType = Field(
        ...,
        description="Account type",
        examples=["credit", "debit"],
    )


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: str | None = None
    number: str | None = None
    holder: str | None = None
    description: str | None = None
    type: AccountType | None = None


class AccountRead(AccountBase):
    id: int
    transactions: list[TransactionRead | None] = []
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
