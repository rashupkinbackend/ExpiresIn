from src.database.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, text, BIGINT
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.dialects.postgresql import UUID
import uuid

if TYPE_CHECKING:
    from src.models.users import UserTable


class DocumentTable(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str] = mapped_column(String(150))
    path: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    expires_at: Mapped[int] = mapped_column(
        BIGINT,
        server_default=text("(EXTRACT(EPOCH FROM (now() + interval '1 day')))::BIGINT"),
    )
    max_downloads: Mapped[int] = mapped_column(server_default=text("1000"))
    downloads_count: Mapped[int] = mapped_column(server_default=text("0"))
    password_hash: Mapped[str | None]

    owner: Mapped["UserTable"] = relationship(back_populates="documents")
