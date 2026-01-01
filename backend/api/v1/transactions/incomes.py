from fastapi import APIRouter, Depends

from core.helpers import get_current_user
from db.models.user import User


router = APIRouter(
    prefix="/transactions/incomes",
    tags=["transactions"],
)


@router.get("/")
async def read_incomes(
    current_user: User = Depends(get_current_user),
):
    return {"message": f"List of incomes for {current_user.username}"}


@router.post("/")
async def create_income(
    current_user: User = Depends(get_current_user),
):
    return {"message": "Income created"}


@router.get("/{income_id}")
async def read_income(
    income_id: int,
    current_user=Depends(get_current_user),
):
    return {"message": f"Details of income {income_id}"}


@router.put("/{income_id}")
async def update_income(
    income_id: int,
    current_user=Depends(get_current_user),
):
    return {"message": f"Income {income_id} updated"}


@router.delete("/{income_id}")
async def delete_income(
    income_id: int,
    current_user=Depends(get_current_user),
):
    return {"message": f"Income {income_id} deleted"}
