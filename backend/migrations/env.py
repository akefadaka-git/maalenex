from alembic import context
from sqlalchemy import engine_from_config, pool
from app.core.config import settings
from app.db.base import Base
from app.db import model_registry  # noqa: F401
config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
target_metadata = Base.metadata

# PostGIS owns this public reference table; it is not application metadata.
POSTGIS_EXTENSION_TABLES = {"spatial_ref_sys"}
LEGACY_MITP_TABLES = {
    "tracking_devices",
    "vehicle_device_assignments",
    "vehicle_telemetry",
}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and reflected and (\n        name in POSTGIS_EXTENSION_TABLES\n        or name in LEGACY_MITP_TABLES\n        or getattr(object, "schema", None) == "geo"\n    ):
        return False
    return True

def run_migrations_offline() -> None:
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"}, compare_type=True, include_object=include_object)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = settings.database_url
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True, include_object=include_object)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
