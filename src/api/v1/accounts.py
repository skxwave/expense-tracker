from fastapi import APIRouter, Depends, status
from dishka.integrations.fastapi import inject, FromDishka

from src.core.helpers import get_current_user
from src.core.schemas.account import AccountCreate, AccountRead
from src.db.models.user import User
from src.services import AccountService

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
)


@router.get(
    "/",
    response_model=list[AccountRead],
)
@inject
async def read_accounts(
    service: FromDishka[AccountService],
    current_user: User = Depends(get_current_user),
):
    return await service.get_accounts(user_id=current_user.id)


@router.get(
    "/{account_id}",
    response_model=AccountRead,
)
@inject
async def read_account(
    service: FromDishka[AccountService],
    account_id: int,
    current_user: User = Depends(get_current_user),
):
    return await service.get_account(
        account_id=account_id,
        user_id=current_user.id,
    )


@router.post(
    "/",
    response_model=AccountRead,
)
@inject
async def create_account(
    service: FromDishka[AccountService],
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
):
    return await service.create(
        data=account_data,
        user_id=current_user.id,
    )
