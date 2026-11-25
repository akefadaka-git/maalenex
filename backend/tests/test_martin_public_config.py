import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_martin_is_explicitly_limited_to_public_geo_views():
    config = (ROOT / "infra/martin/config.yaml").read_text(encoding="utf-8")
    assert "auto_publish: false" in config
    assert "on_invalid: abort" in config
    assert "connection_string: ${MAALENEX_GEO_PUBLIC_DATABASE_URL}" in config
    assert config.count("schema: geo_public") == 6
    assert "schema: geo_internal" not in config
    assert "schema: geo_audit" not in config
    assert "schema: geo\n" not in config
    assert "vehicle_positions" not in config
    assert "legacy_tracking_quarantine" not in config


def test_map_style_uses_only_configured_public_tile_sources():
    style = json.loads(
        (ROOT / "frontend/public/maps/maalenex-public-style.json").read_text(encoding="utf-8")
    )
    expected_sources = {"roads", "boundaries", "routes", "locations", "terminals"}
    assert set(style["sources"]) == expected_sources
    for source in style["sources"].values():
        assert source["type"] == "vector"
        assert source["url"].startswith("/martin/")
        assert "http://" not in source["url"]
        assert "https://" not in source["url"]

    expected_layers = {
        "roads": "roads",
        "boundaries": "boundaries",
        "routes": "routes",
        "locations": "locations",
        "terminals": "terminals",
    }
    for layer in style["layers"]:
        if layer["id"] == "background":
            continue
        assert layer["source"] in expected_layers
        assert layer["source-layer"] == expected_layers[layer["source"]]
