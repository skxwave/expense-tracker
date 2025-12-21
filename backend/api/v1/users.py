import uuid

from fastapi import APIRouter
from fastapi_users import FastAPIUsers

from core.schemas.user import UserCreate, UserRead, UserUpdate
from core.authentication import get_user_manager, jwt_auth_backend
from db.models import User

router = APIRouter(prefix="/users", tags=["users"])
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [jwt_auth_backend],
)

router.include_router(
    fastapi_users.get_auth_router(jwt_auth_backend),
    prefix="/auth/jwt",
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
