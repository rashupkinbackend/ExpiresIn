from src.database.db import new_session
from sqlalchemy import select
from src.models.documents import DocumentTable
from datetime import datetime
from src.storage.storage import client, bucket_name


async def cleanup_expired_documents():
    now = int(datetime.utcnow().timestamp())

    async with new_session() as session:
        query = select(DocumentTable).where(DocumentTable.expires_at < now)
        result = await session.execute(query)
        documents = result.scalars().all()

        if not documents:
            return

        client.remove_objects(bucket_name, [doc.path for doc in documents])

        for doc in documents:
            await session.delete(doc)

        await session.commit()
