import argparse
import logging
import signal
from threading import Event

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.bookings.maintenance import run_booking_maintenance

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("maalenex.booking-maintenance")
shutdown = Event()


def _request_shutdown(signum, frame) -> None:
    logger.info("Received shutdown signal %s.", signum)
    shutdown.set()


def run_once(batch_size: int) -> dict:
    with SessionLocal() as db:
        return run_booking_maintenance(db, batch_size=batch_size)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the synthetic-only MaaleNex Moto booking maintenance worker."
    )
    parser.add_argument("--interval-seconds", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()
    if args.interval_seconds < 5 or args.interval_seconds > 3600:
        raise SystemExit("--interval-seconds must be between 5 and 3600.")
    if args.batch_size < 1 or args.batch_size > 5000:
        raise SystemExit("--batch-size must be between 1 and 5000.")
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise SystemExit("Worker is restricted to development/test synthetic-only environments.")

    signal.signal(signal.SIGINT, _request_shutdown)
    signal.signal(signal.SIGTERM, _request_shutdown)
    logger.info(
        "Booking maintenance worker started; interval=%ss batch_size=%s.",
        args.interval_seconds, args.batch_size,
    )
    while not shutdown.is_set():
        try:
            result = run_once(args.batch_size)
            logger.info("Maintenance cycle completed: %s", result)
        except Exception:
            logger.exception("Maintenance cycle failed; the next cycle will retry.")
        shutdown.wait(args.interval_seconds)
    logger.info("Booking maintenance worker stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
