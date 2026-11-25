from app.db.base import Base
from app.db import model_registry  # noqa: F401


def test_all_migration_backed_application_tables_are_registered():
    expected = {
        "ledger_accounts",
        "ledger_transactions",
        "ledger_postings",
        "passenger_accounts",
        "passenger_credentials",
        "passenger_sessions",
        "passenger_login_attempts",
        "passenger_support_cases",
        "passenger_reports",
        "passenger_report_attachments",
        "passenger_notifications",
        "passenger_notification_preferences",
        "scheduler_leases",
        "scheduler_runs",
        "vehicle_compliance_documents",
        "trip_operational_exceptions",
    }
    assert expected <= set(Base.metadata.tables)


def test_post_migration_columns_are_registered():
    expected_columns = {
        "bookings": {"passenger_account_id"},
        "locations": {"latitude", "longitude", "coordinate_source"},
        "routes": {"geometry", "geometry_source"},
        "seat_layout_versions": {"geometry_metadata"},
    }
    for table_name, columns in expected_columns.items():
        assert columns <= set(Base.metadata.tables[table_name].columns.keys())


def test_booking_owner_foreign_key_preserves_nullable_ownership():
    column = Base.metadata.tables["bookings"].c.passenger_account_id
    assert column.nullable is True
    foreign_key = next(iter(column.foreign_keys))
    assert foreign_key.target_fullname == "passenger_accounts.id"
    assert foreign_key.ondelete == "SET NULL"
