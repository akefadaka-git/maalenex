# ruff: noqa: I001
"""Standalone scheduler process for synthetic development or production operation."""
import logging
import time
from uuid import uuid4

from app.core.config import settings
from app.db.session import SessionLocal
from app.jobs.scheduler_service import run_scheduler_cycle


logger = logging.getLogger("maalenex.scheduler")


def main() -> None:
    supported_runtime = (
        settings.app_env in {"development", "test"} and settings.synthetic_data_only
    ) or (
        settings.app_env == "production" and not settings.synthetic_data_only
    )
    if not supported_runtime:
        raise SystemExit("Scheduler runtime configuration is not supported.")
    if not settings.scheduler_enabled:
        raise SystemExit("Scheduler is disabled. Set SCHEDULER_ENABLED=true for this worker service.")
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
