import os

import pytest
from sqlalchemy import create_engine, text

from app.core.config import settings


pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MITP_BACKFILL_DOWNGRADE") != "1",
    reason="Requires the seeded CI database after downgrading only A3.3.",
)


def test_a33_downgrade_preserves_legacy_source_rows() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM public.tracking_devices")) == 3
        assert connection.scalar(text("SELECT count(*) FROM public.vehicle_device_assignments")) == 3
        assert connection.scalar(text("SELECT count(*) FROM public.vehicle_telemetry")) == 3
        assert connection.scalar(text("SELECT count(*) FROM geo.devices")) == 0
        assert connection.scalar(text("SELECT count(*) FROM geo.device_vehicle_assignments")) == 0
        assert connection.scalar(text("SELECT count(*) FROM geo.vehicle_positions")) == 0
        quarantine_exists = connection.scalar(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'geo'
                  AND table_name = 'legacy_tracking_quarantine'
            )
        """))
        assert quarantine_exists is False
    engine.dispose()
