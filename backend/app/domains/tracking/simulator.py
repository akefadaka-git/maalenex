"""Deterministic synthetic GPS telemetry generation for MITP tests and demos.

This module never reads device sensors, network location, or production records.
"""
from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class SyntheticGpsFix:
    device_id: str
    sequence: int
    recorded_at: datetime
    latitude: float
    longitude: float
    speed_kph: float
    heading_degrees: float
    accuracy_meters: float
    synthetic: bool = True

    def as_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["recorded_at"] = self.recorded_at.isoformat()
        return payload


def generate_route(
    *,
    device_id: str,
    start_latitude: float,
    start_longitude: float,
    point_count: int = 10,
    interval_seconds: int = 15,
    speed_kph: float = 35.0,
    start_at: datetime | None = None,
    seed: int = 1,
) -> list[SyntheticGpsFix]:
    """Generate a reproducible short synthetic route around a supplied test point."""
    if not device_id.strip() or len(device_id) > 80:
        raise ValueError("device_id must contain 1 to 80 characters")
    if not (-90 <= start_latitude <= 90 and -180 <= start_longitude <= 180):
        raise ValueError("starting coordinates are outside valid geographic bounds")
    if not 2 <= point_count <= 500:
        raise ValueError("point_count must be between 2 and 500")
    if not 1 <= interval_seconds <= 3600:
        raise ValueError("interval_seconds must be between 1 and 3600")
    if not 0 <= speed_kph <= 180:
        raise ValueError("speed_kph must be between 0 and 180")

    origin = start_at or datetime.now(UTC)
    if origin.tzinfo is None:
        raise ValueError("start_at must be timezone-aware")
    origin = origin.astimezone(UTC)
    rng = random.Random(seed)
    # Small deterministic north-east movement, approximately 1 degree = 111 km.
    latitude_step = (speed_kph * interval_seconds / 3600 / 111.0) * 0.65
    longitude_scale = max(0.15, math.cos(math.radians(start_latitude)))
    longitude_step = (speed_kph * interval_seconds / 3600 / 111.0) * 0.76 / longitude_scale

    fixes: list[SyntheticGpsFix] = []
    for index in range(point_count):
        jitter_lat = rng.uniform(-0.000015, 0.000015)
        jitter_lon = rng.uniform(-0.000015, 0.000015)
        latitude = start_latitude + index * latitude_step + jitter_lat
        longitude = start_longitude + index * longitude_step + jitter_lon
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise ValueError("generated route crosses geographic bounds")
        fixes.append(SyntheticGpsFix(
            device_id=device_id,
            sequence=index + 1,
            recorded_at=origin + timedelta(seconds=index * interval_seconds),
            latitude=round(latitude, 7),
            longitude=round(longitude, 7),
            speed_kph=round(speed_kph, 2),
            heading_degrees=round(45.0 + rng.uniform(-2.0, 2.0), 2),
            accuracy_meters=round(rng.uniform(3.0, 12.0), 2),
        ))
    return fixes
