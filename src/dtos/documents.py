from pydantic import BaseModel
from datetime import datetime


class DocumentCreateDto(BaseModel):
    max_downloads: int | None = None
    expires_at: int | None = None


class DocumentDto(BaseModel):
    id: int
    owner_id: int
    filename: str
    path: str
    max_downloads: int
    downloads_count: int
    encrypted: bool
    expires_at: int
    created_at: datetime
