from pydantic import BaseModel, Field, EmailStr
from typing import Annotated


class AuthDto(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=100)]


class TokenDto(BaseModel):
    access_token: str
