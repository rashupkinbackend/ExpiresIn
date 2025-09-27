from fastapi import (
    APIRouter,
    File,
    UploadFile,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import StreamingResponse
from minio import S3Error
from src.api.auth import check_jwt, get_tokens, get_data_from_token
from src.dtos.documents import DocumentCreateDto, DocumentDto, DocumentDownloadDto
import json
from sqlalchemy import delete, select
from src.database.db import new_session
from src.models.documents import DocumentTable
import uuid
from src.storage.storage import client, bucket_name
import os
import datetime
from bcrypt import hashpw, checkpw
from src.api.auth import ENCODING, SALT

router = APIRouter(prefix="/documents")


@router.post("/upload", dependencies=[Depends(check_jwt)])
async def upload_file(
    request: Request,
    metadata: str = Form(),
    file: UploadFile = File(),
):
    meta = dict()

    # extracting metadata if has
    if metadata:
        meta = DocumentCreateDto(**json.loads(metadata))
        meta = meta.dict()

    token = get_tokens(request).get("access_token")
    user_data = get_data_from_token(token)

    uuid_name_file = uuid.uuid4()
    user_id = user_data["id"]

    meta["filename"] = file.filename
    meta["owner_id"] = user_data["id"]
    meta["path"] = f"{user_id}/{uuid_name_file}"

    # upload file to storage
    try:
        client.put_object(
            bucket_name, meta["path"], file.file, length=-1, part_size=10 * 1024 * 1024
        )
    except S3Error:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
        )

    async with new_session() as session:
        # hash password
        if meta.get("password"):
            password_hash = hashpw(meta.get("password").encode(ENCODING), SALT)
            meta["password_hash"] = password_hash.decode(ENCODING)
            meta.pop("password")

        document = DocumentTable(**meta)
        session.add(document)

        await session.flush()
        await session.commit()

        return {"id": document.id}


@router.get("/{id}", dependencies=[Depends(check_jwt)])
async def get_info(request: Request, id: str) -> DocumentDto:
    token = get_tokens(request).get("access_token")
    user_data = get_data_from_token(token)

    user_id = user_data["id"]

    async with new_session() as session:
        query = select(DocumentTable).where(DocumentTable.id == id)
        result = await session.execute(query)
        document = result.scalars().first()

        if not document:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

        # only owner can get info
        if document.owner_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient rights")

        return DocumentDto.model_validate(document, from_attributes=True)


# get all documents by owner_id
@router.get("/", dependencies=[Depends(check_jwt)])
async def get_all(request: Request) -> list[DocumentDto]:
    token = get_tokens(request).get("access_token")
    user_data = get_data_from_token(token)

    user_id = user_data["id"]

    async with new_session() as session:
        query = select(DocumentTable).where(DocumentTable.owner_id == user_id)
        result = await session.execute(query)
        documents = result.scalars().all()

        await session.commit()

        return [
            DocumentDto.model_validate(doc, from_attributes=True) for doc in documents
        ]


@router.delete("/{id}", dependencies=[Depends(check_jwt)])
async def delete_file(request: Request, id: str):
    token = get_tokens(request).get("access_token")
    user_data = get_data_from_token(token)

    user_id = user_data["id"]

    async with new_session() as session:
        query = select(DocumentTable).where(DocumentTable.id == id)
        result = await session.execute(query)
        document = result.scalars().first()

        if not document:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

        # only owner can delete
        if document.owner_id != user_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient rights")

        query = delete(DocumentTable).where(DocumentTable.id == id)

        await session.execute(query)
        await session.commit()

        # get file from storage
        try:
            client.remove_object(bucket_name, document.path)
        except S3Error:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
            )

        return {"id": document.id}


@router.post("/{id}/download", dependencies=[Depends(check_jwt)])
async def download_file(id: str, data: DocumentDownloadDto | None = None):
    async with new_session() as session:
        query = select(DocumentTable).where(DocumentTable.id == id)

        result = await session.execute(query)
        document = result.scalars().first()

        if not document:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

        # check password if document has
        if document.password_hash:
            if not data or not data.password:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect password")

            if not checkpw(
                data.password.encode(ENCODING), document.password_hash.encode(ENCODING)
            ):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect password")

        new_downloads_count = document.downloads_count + 1

        # check relevance file (expires_at and max_downloads)
        if (
            document.max_downloads <= new_downloads_count
            or document.expires_at
            < datetime.datetime.timestamp(datetime.datetime.now())
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "The file has expired")

        document.downloads_count = document.downloads_count + 1

        # get file from storage
        try:
            obj = client.get_object(bucket_name, document.path)
        except S3Error:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
            )

        await session.commit()

        return StreamingResponse(
            obj,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(document.filename)}"
            },
        )
