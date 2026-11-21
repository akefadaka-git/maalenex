"""Standalone scheduler process. It is opt-in and synthetic dev/test only."""
import logging
import time
from uuid import uuid4

from app.core.config import settings
from app.db.session import SessionLocal
from app.jobs.scheduler_service import run_scheduler_cycle


logger = logging.getLogger("maalenex.scheduler")


def main() -> None:
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise SystemExit("Scheduler worker is restricted to synthetic development/test mode.")
    if not settings.scheduler_enabled:
        raise SystemExit("Scheduler is disabled. Set MAALENEX_SCHEDULER_ENABLED=true to opt in.")
    worker_id = str(uuid4())
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logger.info("Scheduler worker starting; worker_id=%s", worker_id)
    while True:
        try:
            result = run_scheduler_cycle(
                SessionLocal, worker_id=worker_id,
                batch_size=settings.scheduler_batch_size,
                lease_seconds=settings.scheduler_lease_seconds,
            )
            logger.info("Scheduler cycle completed: %s", result)
        except Exception:
            logger.exception("Scheduler cycle failed; retrying after configured interval")
        time.sleep(settings.scheduler_interval_seconds)


if __name__ == "__main__":
    main()
