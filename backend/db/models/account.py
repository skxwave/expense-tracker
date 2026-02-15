from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .transaction import Transaction


class AccountType(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class Account(TimestampMixin, Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "number", name="uq_user_account_number"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    holder: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    type: Mapped[AccountType] = mapped_column(
        nullable=True,
        default=AccountType.DEBIT,
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="accounts",
    )
