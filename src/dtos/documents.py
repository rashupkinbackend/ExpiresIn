from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DocumentCreateDto(BaseModel):
    max_downloads: int | None = None
    expires_at: int | None = None
    password: str | None = None


class DocumentDto(BaseModel):
    id: UUID
    owner_id: int
    filename: str
    path: str
    max_downloads: int
    downloads_count: int
    encrypted: bool
    expires_at: int
    created_at: datetime


class DocumentDownloadDto(BaseModel):
    password: str | None = None
