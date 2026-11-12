from fastapi.testclient import TestClient

from app.main import app


def test_move_router_registers_authenticated_ride_endpoints():
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/move/rides",
        "/api/v1/move/rides/{ride_id}",
        "/api/v1/move/rides/{ride_id}/transitions",
        "/api/v1/move/rides/{ride_id}/dispatch",
    }
    assert expected.issubset(paths)


def test_move_ride_creation_requires_account_session():
    client = TestClient(app)
    response = client.post(
        "/api/v1/move/rides",
        json={"pickup_area_code": "ET-SO-JINKA", "dropoff_area_code": "ET-SO-KOYBE"},
    )
    assert response.status_code == 401


def test_move_dispatch_requires_staff_session():
    client = TestClient(app)
    response = client.post(
        "/api/v1/move/rides/00000000-0000-0000-0000-000000000001/dispatch",
        json={"driver_account_id": "00000000-0000-0000-0000-000000000002"},
    )
    assert response.status_code == 401
