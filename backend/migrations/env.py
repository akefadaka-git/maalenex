from alembic import context
from sqlalchemy import engine_from_config, pool, text

from app.core.config import settings
from app.db import model_registry  # noqa: F401
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
target_metadata = Base.metadata

# These are legacy MITP source tables. Migration 0021 reads/backfills them into
# the canonical geo schema; they remain preserved as historical source records.
LEGACY_MITP_TABLES = {
    "tracking_devices",
    "vehicle_device_assignments",
    "vehicle_telemetry",
}

# The canonical geo schema is intentionally SQL-first: its PostGIS geometry,
# RLS, views, triggers, grants and publication contracts are managed by
# migrations 0020-0024, not by SQLAlchemy ORM metadata.
MIGRATION_MANAGED_SCHEMAS = {"geo"}

# Populated from pg_depend at runtime. This is extension ownership, not a
# name-based allowlist: only relations PostgreSQL records as members of an
# installed extension are excluded from application metadata parity.
EXTENSION_OWNED_RELATIONS: set[tuple[str | None, str]] = set()


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and reflected:
        schema = getattr(object, "schema", None) or "public"
        if (schema, name) in EXTENSION_OWNED_RELATIONS:
            return False
        if schema in MIGRATION_MANAGED_SCHEMAS:
            return False
        if schema == "public" and name in LEGACY_MITP_TABLES:
            return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = settings.database_url
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        extension_relations = connection.execute(
            text(
                """
                SELECT namespace.nspname, relation.relname,
                       pg_table_is_visible(relation.oid) AS is_visible
                FROM pg_depend AS dependency
                JOIN pg_extension AS extension
                  ON extension.oid = dependency.refobjid
                JOIN pg_class AS relation
                  ON relation.oid = dependency.objid
                JOIN pg_namespace AS namespace
                  ON namespace.oid = relation.relnamespace
                WHERE dependency.classid = 'pg_class'::regclass
                  AND dependency.refclassid = 'pg_extension'::regclass
                  AND dependency.deptype = 'e'
                  AND relation.relkind IN ('r', 'p')
                """
            )
        ).all()
        # SQLAlchemy 2.x autobegins a transaction for the catalog SELECT above.
        # Close that read-only transaction before Alembic opens its migration
        # transaction; otherwise connection teardown rolls back every migration.
        connection.commit()
        EXTENSION_OWNED_RELATIONS.clear()
        for schema_name, relation_name, is_visible in extension_relations:
            EXTENSION_OWNED_RELATIONS.add((schema_name, relation_name))
            # SQLAlchemy reflects relations found through search_path with
            # schema=None; match only the extension object actually visible.
            if is_visible:
                EXTENSION_OWNED_RELATIONS.add((None, relation_name))
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
