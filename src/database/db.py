from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config.config import db_url
from src.logger.logger import logging
from src.config.config import is_dev

logger = logging.getLogger("db")

engine = create_async_engine(db_url, echo=is_dev, pool_pre_ping=True)
new_session = async_sessionmaker(engine, expire_on_commit=False)

logger.info("Database was started successfully")


class Base(DeclarativeBase):
    pass
