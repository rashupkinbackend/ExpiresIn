from fastapi import FastAPI
from src.logger.logger import logging
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from minio import S3Error
from sqlalchemy.exc import SQLAlchemyError
from src.schedulers.scheduler import scheduler
from src.database.db import logger as db_logger
from src.storage.storage import logger as storage_logger
from src.api.api import router

logger = logging.getLogger("app")

app = FastAPI()


# middleware
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        logger.info(f"Request: {request.url} {request.method}")
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as err:
        logger.exception(err)

        return JSONResponse(
            content={"detail": "Internal server error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# exceptions handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    db_logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"Http Exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": f"{exc.detail}"},
    )


@app.exception_handler(S3Error)
async def minio_exception_handler(request: Request, exc: S3Error):
    storage_logger.error(f"MinIO error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Storage error"},
    )


#  schedulers events
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()


@app.on_event("startup")
def startup_event():
    scheduler.start()


app.include_router(router)


logger.info("App was started successfully")
