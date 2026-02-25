from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)
