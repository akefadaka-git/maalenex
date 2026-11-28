from types import SimpleNamespace

from app.routers.passenger_catalog import _location_payload, _published_route_geometry


def test_location_coordinates_require_valid_values_and_source():
    base = dict(id="loc", name="Koybe", location_type="town", latitude=6.9, longitude=36.7, coordinate_source="field_survey")
    assert _location_payload(SimpleNamespace(**base))["coordinates"] == {
        "latitude": 6.9, "longitude": 36.7, "source": "field_survey"
    }
    assert _location_payload(SimpleNamespace(**{**base, "coordinate_source": None}))["coordinates"] is None
    assert _location_payload(SimpleNamespace(**{**base, "latitude": 91}))["coordinates"] is None


def test_route_geometry_requires_line_string_source_and_valid_coordinate_pairs():
    valid = SimpleNamespace(geometry_source="surveyed_gps", geometry={"type": "LineString", "coordinates": [[36.7, 6.9], [36.8, 7.0]]})
    assert _published_route_geometry(valid) == valid.geometry
    assert _published_route_geometry(SimpleNamespace(geometry_source=None, geometry=valid.geometry)) is None
    assert _published_route_geometry(SimpleNamespace(geometry_source="surveyed_gps", geometry={"type": "Point", "coordinates": [36.7, 6.9]})) is None
    assert _published_route_geometry(SimpleNamespace(geometry_source="surveyed_gps", geometry={"type": "LineString", "coordinates": [[36.7, 6.9]]})) is None
    assert _published_route_geometry(SimpleNamespace(geometry_source="surveyed_gps", geometry={"type": "LineString", "coordinates": [[36.7, 96], [36.8, 7.0]]})) is None


def test_operator_confirmed_koybe_boarding_point_coordinates_are_preserved():
    location = SimpleNamespace(
        id="koybe",
        name="Koybe",
        location_type="town",
        latitude=5.7678630,
        longitude=36.7985890,
        coordinate_source="operator_confirmed_terminal_pin",
    )
    assert _location_payload(location)["coordinates"] == {
        "latitude": 5.7678630,
        "longitude": 36.7985890,
        "source": "operator_confirmed_terminal_pin",
    }
