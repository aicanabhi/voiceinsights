"""Transcription worker.

Polls the media table for PENDING rows and runs each one through
transcription + analysis. The table itself is the queue: claiming a row uses
SELECT ... FOR UPDATE SKIP LOCKED, so any number of workers can poll the same
table without two of them picking up the same job.

Run standalone:      python -m app.worker
Run inside the API:  RUN_WORKER_IN_APP=true  (see app/main.py lifespan)
"""

import asyncio
import logging

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.enums import MediaStatus
from app.repositories.media_repository import MediaRepository
from app.services.media_service import MediaService

logger = logging.getLogger("worker")


async def _handle_one() -> bool:
    """Claim and run a single job. Returns False when the queue is empty."""

    async with AsyncSessionLocal() as db:

        media = await MediaRepository.claim_next_pending(db)

        if media is None:
            return False

        logger.info(
            "media %s claimed (attempt %s/%s, provider=%s)",
            media.id,
            media.attempts,
            settings.WORKER_MAX_ATTEMPTS,
            media.provider,
        )

        try:
            await MediaService.process_media(db, media)

            logger.info("media %s completed", media.id)

        except Exception as e:

            await db.rollback()

            message = f"{type(e).__name__}: {e}"

            # Retry until the cap, then park it as FAILED with the reason.
            exhausted = media.attempts >= settings.WORKER_MAX_ATTEMPTS

            await MediaRepository.mark_status(
                db,
                media,
                MediaStatus.FAILED if exhausted else MediaStatus.PENDING,
                error_message=message[:2000],
            )

            logger.warning(
                "media %s %s: %s",
                media.id,
                "failed permanently" if exhausted else "will retry",
                message,
            )

    return True


async def _runner(name: str, stop: asyncio.Event):

    while not stop.is_set():

        try:
            had_work = await _handle_one()

        except Exception:
            # Claiming itself failed (DB down, etc). Back off, stay alive.
            logger.exception("%s: claim loop error", name)
            had_work = False

        if had_work:
            continue

        try:
            await asyncio.wait_for(
                stop.wait(),
                timeout=settings.WORKER_POLL_SECONDS,
            )
        except asyncio.TimeoutError:
            pass


async def run_worker(stop: asyncio.Event | None = None):
    """Start WORKER_CONCURRENCY pollers and run until `stop` is set."""

    stop = stop or asyncio.Event()

    logger.info(
        "worker starting (concurrency=%s, poll=%ss, max_attempts=%s)",
        settings.WORKER_CONCURRENCY,
        settings.WORKER_POLL_SECONDS,
        settings.WORKER_MAX_ATTEMPTS,
    )

    await asyncio.gather(*(
        _runner(f"runner-{i}", stop)
        for i in range(settings.WORKER_CONCURRENCY)
    ))


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("worker stopped")


if __name__ == "__main__":
    main()
