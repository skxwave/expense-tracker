from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from db.models.transaction import TransactionType


class TransactionBase(BaseModel):
    """Base schema for Transaction."""

    amount: Decimal = Field(
        ...,
        gt=0,
        description="Transaction amount (must be positive)",
        examples=[10.75],
    )
    description: str | None = Field(
        None,
        max_length=255,
        description="Transaction description",
        examples=["Lunch at cafe"],
    )
    type: TransactionType = Field(
        ...,
        description="Transaction type (expense or income)",
        examples=["expense", "income"],
    )


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    amount: Decimal | None = Field(
        None,
        gt=0,
        description="Transaction amount (must be positive)",
        examples=[10.75],
    )
    description: str | None = Field(
        None,
        max_length=255,
        description="Transaction description",
        examples=["Lunch at cafe"],
    )


class TransactionRead(TransactionBase):
    """Schema for reading a transaction."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionSummary(BaseModel):
    """Schema for transaction summary statistics."""

    total_expenses: Decimal
    total_incomes: Decimal
    balance: Decimal
    expense_count: int
    income_count: int
