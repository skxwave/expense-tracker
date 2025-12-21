from fastapi_users.authentication import JWTStrategy

from core import settings


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.jwt_secret,
        lifetime_seconds=settings.jwt_lifetime_seconds,
        algorithm=settings.jwt_algorithm,
    )
