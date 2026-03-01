from pwdlib import PasswordHash
from datetime import timedelta

from authx import AuthX, AuthXConfig

from src.db.models.user import User
from src.core.config import settings

auth_config = AuthXConfig()
auth_config.JWT_ALGORITHM = settings.jwt_algorithm
auth_config.JWT_SECRET_KEY = settings.jwt_secret
auth_config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(
    seconds=settings.jwt_access_token_lifetime
)
auth_config.JWT_REFRESH_TOKEN_EXPIRES = timedelta(
    seconds=settings.jwt_refresh_token_lifetime
)
auth_config.JWT_TOKEN_LOCATION = ["headers"]

security = AuthX(config=auth_config)

password_hash = PasswordHash.recommended()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def generate_access_token(user: User) -> str:
    """Generate access token with additional data for a given user."""
    access_token = security.create_access_token(
        uid=str(user.id),
        data={
            "username": user.username,
        },
    )
    return access_token
