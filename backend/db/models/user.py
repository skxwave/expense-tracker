from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
