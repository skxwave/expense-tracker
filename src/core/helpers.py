from authx import RequestToken
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.db import db_session_manager
from src.db.models.user import User
from src.core.auth_config import security


async def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Extract and verify access token from Authorization header."""
    try:
        token = RequestToken(token=credentials.credentials, location="headers")
        payload = security.verify_token(token)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


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


async def get_current_user_id(token_payload=Depends(get_current_token)) -> int:
    """
    Get current user ID from token payload.
    Query the user in your endpoint only if you need the full object.
    """
    return int(token_payload.sub)
