from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import inject, FromDishka

from src.core.helpers import get_current_user
from src.core.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from src.services import TransactionService
from src.db.models import Account

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)


@router.get("/")
async def read_account():
    pass
