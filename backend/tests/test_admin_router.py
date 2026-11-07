from fastapi.testclient import TestClient

from app.main import app


def test_administration_router_is_registered_under_api_prefix():
    paths = app.openapi()["paths"]
    expected = {
        "/api/v1/operators",
        "/api/v1/catalog/routes",
        "/api/v1/vehicles/{vehicle_id}/review",
        "/api/v1/trips/{trip_id}/publish",
        "/api/v1/fares/{fare_id}/versions/{version_id}/review",
        "/api/v1/audit/events",
        "/api/v1/trips/{trip_id}/manifest",
    }
    assert expected.issubset(paths)
    assert any(
        "platform-administration" in operation.get("tags", [])
        for path, operations in paths.items()
        if path in expected
        for operation in operations.values()
    )


def test_administration_mutation_requires_staff_session():
    client = TestClient(app)
    response = client.post(
        "/api/v1/operators",
        json={"display_name": "Synthetic unauthorized operator"},
    )
    assert response.status_code == 401
