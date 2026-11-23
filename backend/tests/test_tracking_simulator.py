from datetime import datetime, timezone

import pytest
from cryptography.fernet import Fernet

from app.domains.tracking.security import (
    decrypt_credential, encrypt_credential, sign_telemetry,
    verify_telemetry_signature,
)
from app.domains.tracking.simulator import generate_route


def test_synthetic_route_is_deterministic_and_monotonic():
    start = datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)
    first = generate_route(
        device_id="SIM-GPS-0001", start_latitude=6.25, start_longitude=36.88,
        point_count=5, interval_seconds=15, start_at=start, seed=42,
    )
    second = generate_route(
        device_id="SIM-GPS-0001", start_latitude=6.25, start_longitude=36.88,
        point_count=5, interval_seconds=15, start_at=start, seed=42,
    )
    assert first == second
    assert [fix.sequence for fix in first] == [1, 2, 3, 4, 5]
    assert all(fix.synthetic for fix in first)
    assert all(fix.recorded_at.tzinfo is not None for fix in first)
    assert all(-90 <= fix.latitude <= 90 and -180 <= fix.longitude <= 180 for fix in first)


def test_simulator_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        generate_route(device_id="", start_latitude=6, start_longitude=36)
    with pytest.raises(ValueError):
        generate_route(device_id="SIM-1", start_latitude=91, start_longitude=36)
    with pytest.raises(ValueError):
        generate_route(device_id="SIM-1", start_latitude=6, start_longitude=36, point_count=1)
    with pytest.raises(ValueError):
        generate_route(
            device_id="SIM-1", start_latitude=6, start_longitude=36,
            start_at=datetime(2026, 11, 23),
        )


def test_device_credential_is_encrypted_and_round_trips():
    key = Fernet.generate_key().decode("ascii")
    credential = "synthetic-device-credential-value-0001"
    ciphertext = encrypt_credential(credential, key)
    assert credential not in ciphertext
    assert decrypt_credential(ciphertext, key) == credential
    with pytest.raises(ValueError):
        decrypt_credential(ciphertext, Fernet.generate_key().decode("ascii"))


def test_device_telemetry_signature_binds_timestamp_and_exact_body():
    credential = "synthetic-device-credential-value-0001"
    body = b'{"sequence":1,"latitude":6.25,"longitude":36.88}'
    timestamp = "1795420800"
    signature = sign_telemetry(credential, timestamp, body)
    assert verify_telemetry_signature(credential, timestamp, body, signature)
    assert not verify_telemetry_signature(credential, "1795420801", body, signature)
    assert not verify_telemetry_signature(credential, timestamp, body + b" ", signature)
    assert not verify_telemetry_signature(credential, timestamp, body, "invalid")
