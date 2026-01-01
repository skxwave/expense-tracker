from authx import RequestToken
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.exc import IntegrityError

from core import (
    verify_password,
    security,
    get_current_token,
    generate_access_token,
    get_password_hash,
)
from core.schemas.user import (
    UserCreate,
    UserLoginRequest,
    UserRead,
    UserLoginResponse,
    UserRefreshResponse,
)
from db.repositories import UserRepository, get_user_repository

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_create: UserCreate,
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserRead:
    """Register a new user."""
    try:
        user = await user_repository.create(
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            username=user_create.username,
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
        )
        return UserRead.model_validate(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )


@router.post("/auth/login", response_model=UserLoginResponse)
async def login(
    user_login: UserLoginRequest,
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserLoginResponse:
    """Authenticate a user and return access and refresh tokens."""
    user = await user_repository.get_by_username(user_login.username)

    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
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
    user_repository: UserRepository = Depends(get_user_repository),
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
            detail=f"Invalid or expired refresh token. Details: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists
    user_id = int(payload.sub)
    user = await user_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # Create new token
    access_token = generate_access_token(user)

    return UserRefreshResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_current_user(
    token_payload=Depends(get_current_token),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserRead:
    """Get the current authenticated user from the access token."""
    # Extract user ID from token payload
    user_id = int(token_payload.sub)

    # Fetch user from database
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserRead.model_validate(user)
