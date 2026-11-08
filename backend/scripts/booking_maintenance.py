import argparse
import json

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.bookings.maintenance import run_booking_maintenance


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded MaaleNex Moto booking maintenance.")
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()
    if settings.app_env not in {"development", "test"} or not settings.synthetic_data_only:
        raise SystemExit("Maintenance CLI is restricted to development/test synthetic-only environments.")
    with SessionLocal() as db:
        result = run_booking_maintenance(db, batch_size=args.batch_size)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
