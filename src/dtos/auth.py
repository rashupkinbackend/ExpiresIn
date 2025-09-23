from pydantic import BaseModel


class AuthDto(BaseModel):
    email: str
    password: str


class TokenDto(BaseModel):
    access_token: str
