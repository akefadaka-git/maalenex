from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def migration_scripts() -> ScriptDirectory:
    config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(config_path))
    config.set_main_option("script_location", str(config_path.parent / "migrations"))
    return ScriptDirectory.from_config(config)


def test_consolidated_migration_history_has_one_head() -> None:
    assert migration_scripts().get_heads() == ["0024_geo_provenance_licensing"]


def test_merge_revision_preserves_both_stream_heads() -> None:
    merge = migration_scripts().get_revision("0019_merge_passenger_mitp")
    assert merge is not None
    assert merge.down_revision == (
        "0018_koybe_boarding_point",
        "0008_mitp_tracking",
    )


def test_canonical_postgis_schema_follows_the_merge_revision() -> None:
    spatial = migration_scripts().get_revision("0020_canonical_postgis_schema")
    assert spatial is not None
    assert spatial.down_revision == "0019_merge_passenger_mitp"


def test_mitp_backfill_follows_canonical_geo_schema() -> None:
    backfill = migration_scripts().get_revision("0021_mitp_tracking_to_geo")
    assert backfill is not None
    assert backfill.down_revision == "0020_canonical_postgis_schema"


def test_publication_views_follow_mitp_backfill() -> None:
    publication = migration_scripts().get_revision("0022_geo_publication_views")
    assert publication is not None
    assert publication.down_revision == "0021_mitp_tracking_to_geo"

def test_tenant_rls_follows_publication_views() -> None:
    rls = migration_scripts().get_revision("0023_geo_tenant_rls_permissions")
    assert rls is not None
    assert rls.down_revision == "0022_geo_publication_views"
