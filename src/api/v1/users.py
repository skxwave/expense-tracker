from fastapi import APIRouter, status, Depends

from src.core import get_current_token
from src.core.schemas.user import (
    UserCreate,
    UserLoginRequest,
    UserRead,
    UserLoginResponse,
    UserRefreshResponse,
)
from src.services import UserService, get_user_service, AuthService, get_auth_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/auth/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_create: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """Register a new user."""
    return await service.register_user(user_create)


@router.post("/auth/login", response_model=UserLoginResponse)
async def login(
    user_login: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserLoginResponse:
    """Authenticate a user and return access and refresh tokens."""
    return await auth_service.authenticate_and_create_token_pair(
        user_login.username,
        user_login.password,
    )


@router.post("/auth/refresh", response_model=UserRefreshResponse)
async def refresh_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRefreshResponse:
    """Refresh access token using refresh token."""
    return await auth_service.refresh_access_token(token)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    token_payload=Depends(get_current_token),
    user_service: UserService = Depends(get_user_service),
) -> UserRead:
    """Get the current authenticated user from the access token."""
    return await user_service.get_by_id(int(token_payload.sub))
