from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from uuid import UUID


class DocumentCreateDto(BaseModel):
    max_downloads: int | None = None
    expires_at: int | None = None
    password: Annotated[str | None, Field(min_length=8, max_length=100)] = None


class DocumentDto(BaseModel):
    id: UUID
    owner_id: int
    filename: str
    path: str
    max_downloads: int
    downloads_count: int
    expires_at: int
    created_at: datetime

    model_config = {"from_attributes": True, "extra": "ignore"}


class DocumentDownloadDto(BaseModel):
    password: Annotated[str | None, Field(min_length=8, max_length=100)] = None
