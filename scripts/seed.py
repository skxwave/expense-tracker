"""
Seed script: creates one test user, 3 accounts, and 30 transactions spread
across the last 365 days.

Usage:
    uv run python scripts/seed.py

Credentials after seeding:
    username : seed_user
    password : SeedPass123!
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta, timezone

# Ensure the project root (parent of scripts/) is on sys.path so that `src`
# is importable whether the script is run from inside or outside Docker.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.auth_config import get_password_hash
from src.core.config import settings
from src.db.models import Account, Transaction, User
from src.models.enums import AccountType, TransactionType

# ── seed data ────────────────────────────────────────────────────────────────

SEED_USERNAME = "seed_user"
SEED_PASSWORD = "SeedPass123!"

ACCOUNTS_DATA = [
    {
        "name": "Main Checking",
        "number": "1000000001",
        "holder": "Seed User",
        "value": "5000.00",
        "description": "Primary everyday account",
        "type": AccountType.DEBIT,
    },
    {
        "name": "Savings",
        "number": "1000000002",
        "holder": "Seed User",
        "value": "12000.00",
        "description": "Long-term savings",
        "type": AccountType.DEBIT,
    },
    {
        "name": "Credit Card",
        "number": "1000000003",
        "holder": "Seed User",
        "value": "2000.00",
        "description": "Monthly credit card",
        "type": AccountType.CREDIT,
    },
]

TRANSACTION_TEMPLATES = [
    # (description, type, amount_range)
    ("Grocery shopping", TransactionType.EXPENSE, (20, 150)),
    ("Restaurant dinner", TransactionType.EXPENSE, (15, 80)),
    ("Monthly salary", TransactionType.INCOME, (2000, 4000)),
    ("Netflix subscription", TransactionType.EXPENSE, (15, 20)),
    ("Electricity bill", TransactionType.EXPENSE, (50, 180)),
    ("Freelance payment", TransactionType.INCOME, (200, 1500)),
    ("Gym membership", TransactionType.EXPENSE, (30, 60)),
    ("Coffee shop", TransactionType.EXPENSE, (4, 20)),
    ("Online shopping", TransactionType.EXPENSE, (20, 300)),
    ("Dividend income", TransactionType.INCOME, (50, 500)),
    ("Internet bill", TransactionType.EXPENSE, (30, 70)),
    ("Taxi / Uber", TransactionType.EXPENSE, (8, 50)),
    ("Bonus payment", TransactionType.INCOME, (300, 1000)),
    ("Movie tickets", TransactionType.EXPENSE, (10, 40)),
    ("Pharmacy", TransactionType.EXPENSE, (10, 80)),
    ("Book purchase", TransactionType.EXPENSE, (10, 50)),
    ("Rent payment", TransactionType.EXPENSE, (600, 1500)),
    ("Side project income", TransactionType.INCOME, (100, 800)),
    ("Clothing store", TransactionType.EXPENSE, (40, 200)),
    ("Birthday gift", TransactionType.EXPENSE, (20, 100)),
    ("Stock sale", TransactionType.INCOME, (100, 2000)),
    ("Gas station", TransactionType.EXPENSE, (30, 80)),
    ("Takeaway food", TransactionType.EXPENSE, (10, 40)),
    ("Music streaming", TransactionType.EXPENSE, (5, 15)),
    ("Home repair", TransactionType.EXPENSE, (50, 400)),
    ("Consulting fee", TransactionType.INCOME, (500, 2000)),
    ("Charity donation", TransactionType.EXPENSE, (10, 100)),
    ("Parking fee", TransactionType.EXPENSE, (5, 30)),
    ("ATM withdrawal", TransactionType.EXPENSE, (50, 200)),
    ("Interest income", TransactionType.INCOME, (5, 50)),
]


# ── helpers ───────────────────────────────────────────────────────────────────


def random_date_within_days(days: int) -> datetime:
    delta = random.randint(0, days - 1)
    return datetime.now(timezone.utc) - timedelta(days=delta)


# ── seed logic ────────────────────────────────────────────────────────────────


async def seed(session: AsyncSession) -> None:
    # 1. Remove existing seed user (cascade deletes accounts + transactions)
    await session.execute(
        text("DELETE FROM users WHERE username = :u"), {"u": SEED_USERNAME}
    )
    await session.flush()

    # 2. Create user
    user = User(
        first_name="Seed",
        last_name="User",
        username=SEED_USERNAME,
        email="seed@example.com",
        hashed_password=get_password_hash(SEED_PASSWORD),
        is_active=True,
        is_verified=True,
    )
    session.add(user)
    await session.flush()  # populate user.id

    # 3. Create accounts
    accounts: list[Account] = []
    for data in ACCOUNTS_DATA:
        acc = Account(**data, user_id=user.id)
        session.add(acc)
        accounts.append(acc)
    await session.flush()  # populate account ids

    # 4. Create transactions — at least 30, spread over 365 days
    templates = TRANSACTION_TEMPLATES.copy()
    random.shuffle(templates)

    for i, (desc, tx_type, (lo, hi)) in enumerate(templates):
        amount = round(random.uniform(lo, hi), 2)
        account = accounts[i % len(accounts)]
        created = random_date_within_days(365)

        tx = Transaction(
            amount=str(amount),
            description=desc,
            type=tx_type,
            account_id=account.id,
            user_id=user.id,
        )
        session.add(tx)

        # override created_at so it appears spread over the year
        await session.flush()
        await session.execute(
            text("UPDATE transactions SET created_at = :dt WHERE id = :id"),
            {"dt": created, "id": tx.id},
        )

    await session.commit()
    print(f"Seeded user '{SEED_USERNAME}' with {len(templates)} transactions.")
    print(f"  Login with  username={SEED_USERNAME}  password={SEED_PASSWORD}")


async def main() -> None:
    engine = create_async_engine(settings.db_url, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
