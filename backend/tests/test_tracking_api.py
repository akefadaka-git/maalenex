from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.domains.tracking.schemas import TelemetryPayload
from app.main import app


def test_tracking_routes_are_registered():
    paths = app.openapi()["paths"]
    assert "/api/v1/tracking/devices" in paths
    assert "/api/v1/tracking/devices/{device_id}/assignments/end" in paths
    assert "/api/v1/tracking/devices/{device_id}/assignments" in paths
    assert "/api/v1/tracking/devices/{device_id}/credentials/rotate" in paths
    assert "/api/v1/tracking/telemetry" in paths
    assert "/api/v1/tracking/vehicles/{vehicle_id}/latest" in paths


def test_telemetry_ingestion_requires_device_authentication_headers():
    response = TestClient(app).post("/api/v1/tracking/telemetry", content=b"{}")
    assert response.status_code == 401


def test_telemetry_schema_rejects_naive_time_and_out_of_range_coordinates():
    with pytest.raises(ValidationError):
        TelemetryPayload(
            sequence=1, recorded_at=datetime(2026, 11, 23, 8, 0),
            latitude=6.25, longitude=36.88, speed_kph=10,
            heading_degrees=90, accuracy_meters=5,
        )
    with pytest.raises(ValidationError):
        TelemetryPayload(
            sequence=1, recorded_at="2026-11-23T08:00:00Z",
            latitude=91, longitude=36.88, speed_kph=10,
            heading_degrees=90, accuracy_meters=5,
        )
