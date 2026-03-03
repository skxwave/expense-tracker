from enum import StrEnum


class TransactionType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"


class AccountType(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"
