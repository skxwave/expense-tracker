from fastapi import Depends, HTTPException, status

from db import db_session_manager
from db.models.user import User
from .auth_config import get_current_token


async def get_current_user(
    token_payload=Depends(get_current_token),
    session=Depends(db_session_manager.get_async_session),
) -> User:
    """Get the current authenticated user from token."""
    from sqlalchemy import select

    user_id = token_payload.sub

    async with session as session:
        user = await session.scalar(select(User).where(User.id == int(user_id)))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
