from src.database.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str]
