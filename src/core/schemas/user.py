from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Only letters, digits, and underscores are allowed",
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Must be at least 8 characters",
    )


class UserUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)


class UserLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
