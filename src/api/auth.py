from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from src.dtos.auth import AuthDto, TokenDto
from src.database.db import new_session
from src.models.users import UserTable
from sqlalchemy import select
from bcrypt import hashpw, gensalt, checkpw
from jwt import encode, decode, ExpiredSignatureError
from src.config.config import (
    jwt_access_expires_in,
    jwt_refresh_expires_in,
    jwt_secret_key,
    is_dev,
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth")

SALT = gensalt()
ALGORITHM = "HS256"
ENCODING = "utf-8"


def get_tokens(user_data: dict):
    access_token_data = user_data.copy()
    refresh_token_data = user_data.copy()

    access_token_data["exp"] = (
        datetime.now() + timedelta(minutes=int(jwt_access_expires_in))
    ).timestamp()
    refresh_token_data["exp"] = (
        datetime.now() + timedelta(days=int(jwt_refresh_expires_in))
    ).timestamp()

    return {
        "access_token": encode(access_token_data, jwt_secret_key, algorithm=ALGORITHM),
        "refresh_token": encode(
            refresh_token_data, jwt_secret_key, algorithm=ALGORITHM
        ),
    }


async def check_and_get_new_tokens(request: Request):
    body = await request.json()
    token = body["token"]

    try:
        user_data = decode(token, jwt_secret_key, algorithms=[ALGORITHM])
        return get_tokens(user_data)
    except ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Token's lifespan has expired"
        )


def set_refresh_token(response: Response, token: str) -> Response:
    response.set_cookie(
        "refresh_token",
        token,
        httponly=True,
        samesite="strict",
        secure=not is_dev,
    )


@router.post("/register")
async def register(data: AuthDto, response: Response) -> TokenDto:
    async with new_session() as session:
        query = select(UserTable).where(UserTable.email == data.email)
        result = await session.execute(query)
        user = result.first()

        if user is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "User already exists")

        password_hash = hashpw(data.password.encode(ENCODING), SALT)
        user = UserTable(email=data.email, password_hash=password_hash.decode(ENCODING))

        session.add(user)
        await session.flush()
        await session.commit()

        tokens = get_tokens({"id": user.id})
        response = set_refresh_token(response, tokens.get("refresh_token"))

        return {"access_token": tokens.get("access_token")}


@router.post("/login")
async def login(data: AuthDto, response: Response) -> TokenDto:
    async with new_session() as session:
        query = select(UserTable).where(UserTable.email == data.email)
        result = await session.execute(query)
        user = result.scalars().first()

        if user is None or not checkpw(
            data.password.encode("utf-8"), user.password_hash.encode(ENCODING)
        ):

            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid data")

        await session.commit()

        tokens = get_tokens({"id": user.id})
        response = set_refresh_token(response, tokens.get("refresh_token"))

        return {"access_token": tokens.get("access_token")}


@router.post(
    "/refresh",
)
async def refresh_token(
    response: Response, tokens: TokenDto = Depends(check_and_get_new_tokens)
) -> TokenDto:
    response = set_refresh_token(response, tokens.get("refresh_token"))

    return {"access_token": tokens.get("access_token")}
