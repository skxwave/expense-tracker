from fastapi import Depends

from .user_service import UserService
from .auth_service import AuthService
from src.db.repositories import UserRepository, get_user_repository


def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)


def get_auth_service(user_service: UserService = Depends(get_user_service)):
    return AuthService(user_service)
