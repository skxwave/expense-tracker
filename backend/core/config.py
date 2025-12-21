from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration settings for the application."""
    debug: bool = True
    db_url: str

    secret_key: str
    jwt_secret: str
    jwt_lifetime_seconds: int = 3600
    jwt_algorithm: str = "HS256"
    reset_password_token_secret: str
    verification_token_secret: str

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
    )


@lru_cache()
def get_config() -> Config:
    """Retrieve the application configuration."""
    return Config()


settings = get_config()
