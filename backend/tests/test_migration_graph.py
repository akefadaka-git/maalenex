from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def migration_scripts() -> ScriptDirectory:
    config_path = Path(__file__).resolve().parents[1] / "alembic.ini"
    return ScriptDirectory.from_config(Config(str(config_path)))


def test_consolidated_migration_history_has_one_head() -> None:
    assert migration_scripts().get_heads() == ["0019_merge_passenger_mitp"]


def test_merge_revision_preserves_both_stream_heads() -> None:
    merge = migration_scripts().get_revision("0019_merge_passenger_mitp")
    assert merge is not None
    assert merge.down_revision == (
        "0018_koybe_boarding_point",
        "0008_mitp_tracking",
    )
