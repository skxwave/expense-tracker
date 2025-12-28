from authx import RequestToken
from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core import (
    get_password_hash,
    verify_password,
    security,
    get_current_token,
    generate_access_token,
)
from core.schemas.user import (
    UserCreate,
    UserLoginRequest,
    UserRead,
    UserLoginResponse,
    UserRefreshResponse,
)
from db import db_session_manager
from db.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/auth/register", response_model=UserRead)
async def register_user(
    user_create: UserCreate,
    session: AsyncSession = Depends(db_session_manager.get_async_session),
) -> UserRead:
    """Register a new user."""
    try:
        new_user = User(
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            username=user_create.username,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return UserRead(**new_user.__dict__)
    except Exception as e:
        await session.rollback()
        raise e


@router.post("/auth/login", response_model=UserLoginResponse)
async def login(
    user_login: UserLoginRequest,
    session: AsyncSession = Depends(db_session_manager.get_async_session),
) -> UserLoginResponse:
    """Authenticate a user and return access and refresh tokens."""
    user = await session.scalar(
        select(User).where(User.username == user_login.username)
    )

    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = generate_access_token(user)
    refresh_token = security.create_refresh_token(uid=str(user.id))

    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/auth/refresh", response_model=UserRefreshResponse)
async def refresh_token(
    token: str,
    session: AsyncSession = Depends(db_session_manager.get_async_session),
) -> UserRefreshResponse:
    """Refresh access token using refresh token."""
    # Extract user ID from token payload
    converted_token = RequestToken(token=token, location="json", type="refresh")

    # Verify refresh token
    try:
        payload = security.verify_token(converted_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token. Details: " + str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists
    user_id = payload.sub
    user = await session.get(User, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create new token
    access_token = generate_access_token(user)

    return UserRefreshResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    token_payload=Depends(get_current_token),
    session: AsyncSession = Depends(db_session_manager.get_async_session),
) -> UserRead:
    """Get the current authenticated user from the access token."""
    # Extract user ID from token payload
    user_id = token_payload.sub

    # Fetch user from database
    user = await session.scalar(select(User).where(User.id == int(user_id)))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserRead(**user.__dict__)
