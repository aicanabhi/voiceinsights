import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.mongo import init_mongo_indexes
from app.worker import run_worker

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_mongo_indexes()

    worker_stop = None
    worker_task = None

    if settings.RUN_WORKER_IN_APP:
        # Dev convenience. In production run `python -m app.worker` separately
        # so a busy worker cannot starve the API.
        logger.info("starting transcription worker inside the API process")
        worker_stop = asyncio.Event()
        worker_task = asyncio.create_task(run_worker(worker_stop))

    try:
        yield

    finally:
        if worker_task is not None:
            worker_stop.set()
            worker_task.cancel()

            try:
                await worker_task
            except (asyncio.CancelledError, Exception):
                pass


app = FastAPI(
    title="VoiceInsights AI",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message": "VoiceInsights Backend Running 🚀"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


app.include_router(
    api_router,
    prefix="/api/v1"
)