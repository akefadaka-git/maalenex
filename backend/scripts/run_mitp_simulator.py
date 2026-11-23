"""Send deterministic synthetic GPS fixes to a local MITP development API.

Example:
python scripts/run_mitp_simulator.py --url http://127.0.0.1:8000 --device-id SIM-GPS-0001 \
  --credential <one-time-device-credential> --latitude 6.25 --longitude 36.88
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.domains.tracking.security import sign_telemetry
from app.domains.tracking.simulator import generate_route


def main() -> int:
    parser = argparse.ArgumentParser(description="MITP synthetic GPS-device simulator")
    parser.add_argument("--url", required=True, help="Local API base URL, e.g. http://127.0.0.1:8000")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--credential", required=True, help="Synthetic device credential; never logged")
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--points", type=int, default=5)
    parser.add_argument("--interval-seconds", type=int, default=15)
    parser.add_argument("--speed-kph", type=float, default=25)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        parser.error("--url must be an absolute HTTP(S) URL")
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("unencrypted HTTP is allowed only for loopback development")

    fixes = generate_route(
        device_id=args.device_id,
        start_latitude=args.latitude,
        start_longitude=args.longitude,
        point_count=args.points,
        interval_seconds=args.interval_seconds,
        speed_kph=args.speed_kph,
        start_at=datetime.now(timezone.utc),
        seed=args.seed,
    )
    endpoint = args.url.rstrip("/") + "/api/v1/tracking/telemetry"
    for fix in fixes:
        payload = fix.as_payload()
        body = json.dumps({
            "sequence": payload["sequence"],
            "recorded_at": payload["recorded_at"],
            "latitude": payload["latitude"],
            "longitude": payload["longitude"],
            "speed_kph": payload["speed_kph"],
            "heading_degrees": payload["heading_degrees"],
            "accuracy_meters": payload["accuracy_meters"],
        }, separators=(",", ":")).encode("utf-8")
        request_timestamp = str(int(time.time()))
        signature = sign_telemetry(args.credential, request_timestamp, body)
        request = Request(
            endpoint,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-MITP-Device-ID": args.device_id,
                "X-MITP-Timestamp": request_timestamp,
                "X-MITP-Signature": signature,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                print("sequence", fix.sequence, "HTTP", response.status)
        except HTTPError as exc:
            print("sequence", fix.sequence, "HTTP", exc.code, exc.read(512).decode("utf-8", "replace"))
            return 1
        except (URLError, TimeoutError) as exc:
            print("telemetry delivery failed:", type(exc).__name__)
            return 1
        if fix is not fixes[-1]:
            time.sleep(args.interval_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
