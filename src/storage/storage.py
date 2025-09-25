from minio import Minio
from minio.error import S3Error
from src.config.config import (
    storage_host,
    storage_port,
    storage_access_key,
    storage_secret_key,
)
from src.logger.logger import logging
import sys

logger = logging.getLogger("storage")

try:
    # connection to miniO
    client = Minio(
        f"{storage_host}:{storage_port}",
        access_key=storage_access_key,
        secret_key=storage_secret_key,
        secure=False,
    )

    # check miniO connection
    client.list_buckets()
    logger.info("MiniO client started successfully")
except S3Error as err:
    logger.fatal(err)
    sys.exit(1)
except Exception as err:
    logger.fatal(err)
    sys.exit(1)


bucket_name = "expiresin"
