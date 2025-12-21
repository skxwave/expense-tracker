import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    first_name: str
    last_name: str
    username: str


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
