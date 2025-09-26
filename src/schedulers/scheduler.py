from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.schedulers.clean_documents import cleanup_expired_documents
from src.schedulers.clean_log import cleanup_log
from datetime import datetime

scheduler = AsyncIOScheduler()
scheduler.add_job(
    cleanup_expired_documents, "interval", next_run_time=datetime.now(), days=1
)
scheduler.add_job(cleanup_log, "interval", hours=12)
