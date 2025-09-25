from minio import Minio
from minio.error import S3Error
from src.config.config import (
    storage_host,
    storage_port,
    storage_access_key,
    storage_secret_key,
    is_dev,
)

client = Minio(
    f"{storage_host}:{storage_port}",
    access_key=storage_access_key,
    secret_key=storage_secret_key,
    secure=not is_dev,
)

bucket_name = "expiresin"
