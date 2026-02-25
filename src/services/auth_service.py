from authx import RequestToken

from .user_service import UserService
from .base_service import BaseService
from src.core.auth_config import verify_password, generate_access_token, security
from src.core.exceptions import InvalidCredentialsError, EntityNotFoundError


class AuthService(BaseService):
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_and_create_token_pair(
        self,
        username: str,
        password: str,
    ) -> dict[str, str]:
        user = await self.user_service.get_by_username(username)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid credentials")

        return {
            "access_token": generate_access_token(user),
            "refresh_token": security.create_refresh_token(uid=str(user.id)),
            "token_type": "Bearer",
        }

    async def refresh_access_token(
        self,
        token: str,
    ):
        converted_token = RequestToken(token=token, location="json", type="refresh")

        try:
            payload = security.verify_token(converted_token)
        except:
            raise InvalidCredentialsError("Invalid or expired token.")

        user = await self.user_service.get_by_id(int(payload.sub))

        if not user:
            raise EntityNotFoundError("User not found")

        return {
            "access_token": generate_access_token(user),
            "token_type": "Bearer",
        }
