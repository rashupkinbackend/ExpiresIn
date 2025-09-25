from fastapi import APIRouter, File, UploadFile, Depends, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from minio import S3Error
from src.api.auth import check_jwt, get_tokens, get_data_from_token
from src.dtos.documents import DocumentCreateDto, DocumentDto
import json
from sqlalchemy import delete, select
from src.database.db import new_session
from src.models.documents import DocumentTable
import uuid
from src.storage.storage import client, bucket_name
import os
import datetime

router = APIRouter(prefix="/documents")


@router.post("/upload", dependencies=[Depends(check_jwt)])
async def upload_file(
    request: Request,
    metadata: str = Form(),
    file: UploadFile = File(),
):
    token = get_tokens(request).get("access_token")
    user_data = get_data_from_token(token)

    uuid_name_file = uuid.uuid4()
    user_id = user_data["id"]

    meta = DocumentCreateDto(**json.loads(metadata))
    meta = meta.dict()
    meta["filename"] = file.filename
    meta["owner_id"] = user_data["id"]
    meta["path"] = f"{user_id}/{uuid_name_file}"

    try:
        client.put_object(
            bucket_name, meta["path"], file.file, length=-1, part_size=10 * 1024 * 1024
        )
    except S3Error:
        raise HTTPException(500, "Internal server error")

    async with new_session() as session:
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
            raise HTTPException(404, "Document not found")

        if document.owner_id != user_id:
            raise HTTPException(403, "Insufficient rights")

        await session.commit()

        return DocumentDto.model_validate(document, from_attributes=True)


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
            raise HTTPException(404, "Document not found")

        if document.owner_id != user_id:
            raise HTTPException(403, "Insufficient rights")

        query = delete(DocumentTable).where(DocumentTable.id == id)

        await session.execute(query)
        await session.commit()

        try:
            client.remove_object(bucket_name, document.path)
        except S3Error:
            raise HTTPException(500, "Internal server error")

        return {"id": document.id}


@router.get("/{id}/download", dependencies=[Depends(check_jwt)])
async def download_file(id: str):
    async with new_session() as session:
        query = select(DocumentTable).where(DocumentTable.id == id)

        result = await session.execute(query)
        document = result.scalars().first()

        if not document:
            raise HTTPException(404, "Document not found")

        new_downloads_count = document.downloads_count + 1

        if (
            document.max_downloads <= new_downloads_count
            or document.expires_at
            < datetime.datetime.timestamp(datetime.datetime.now())
        ):
            raise HTTPException(400, "The file has expired")

        document.downloads_count = document.downloads_count + 1

        try:
            obj = client.get_object(bucket_name, document.path)
        except S3Error:
            raise HTTPException(500, "Internal server error")

        await session.commit()

        return StreamingResponse(
            obj,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(document.filename)}"
            },
        )
