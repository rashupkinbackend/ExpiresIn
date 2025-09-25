from src.database.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from src.models.documents import DocumentTable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.documents import DocumentTable


class UserTable(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str]

    documents: Mapped[list["DocumentTable"]] = relationship(back_populates="owner")
