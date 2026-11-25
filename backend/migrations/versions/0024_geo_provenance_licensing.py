"""Add enforceable geographic provenance and license-review controls.

Revision ID: 0024_geo_provenance_licensing
Revises: 0023_geo_tenant_rls_permissions

Existing unreviewed sources are made ineligible for public publication. No
license or source authority is inferred during this migration.
"""
from alembic import op

revision = "0024_geo_provenance_licensing"
down_revision = "0023_geo_tenant_rls_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
ALTER TABLE geo.data_sources
    ADD COLUMN license_review_status varchar(24) NOT NULL DEFAULT 'pending',
    ADD COLUMN license_reviewed_at timestamptz,
    ADD COLUMN license_reviewed_by varchar(128),
    ADD COLUMN source_method varchar(48),
    ADD COLUMN evidence_reference text,
    ADD COLUMN verification_notes text
""")
    op.execute("""
ALTER TABLE geo.data_sources
    ADD CONSTRAINT ck_geo_source_license_review_status
    CHECK (license_review_status IN ('pending', 'approved', 'denied', 'restricted'))
""")
    op.execute("""
ALTER TABLE geo.data_sources
    ADD CONSTRAINT ck_geo_source_license_review_evidence
    CHECK (
        (license_review_status = 'approved'
         AND license_reviewed_at IS NOT NULL
         AND NULLIF(pg_catalog.btrim(license_reviewed_by), '') IS NOT NULL)
        OR license_review_status <> 'approved'
    )
""")

    # Never infer reuse rights for previously eligible sources. Fail closed:
    # an authorized catalog reviewer must explicitly review and re-approve.
    op.execute("""
UPDATE geo.data_sources
SET publication_eligible = false,
    license_review_status = 'pending',
    license_reviewed_at = NULL,
    license_reviewed_by = NULL
WHERE publication_eligible = true
""")

    op.execute("""
CREATE OR REPLACE FUNCTION geo.enforce_source_publication_eligibility()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $geo_source_guard$
BEGIN
    IF NEW.publication_eligible AND (
        NEW.verification_status <> 'verified'
        OR NEW.verified_at IS NULL
        OR NEW.license_review_status <> 'approved'
        OR NEW.license_reviewed_at IS NULL
        OR NEW.license_reviewed_by IS NULL
        OR NULLIF(pg_catalog.btrim(NEW.license_identifier), '') IS NULL
        OR NULLIF(pg_catalog.btrim(NEW.license_name), '') IS NULL
        OR NULLIF(pg_catalog.btrim(NEW.attribution_text), '') IS NULL
    ) THEN
        RAISE EXCEPTION
            'geographic source requires verified provenance and approved license review before publication eligibility';
    END IF;
    RETURN NEW;
END;
$geo_source_guard$
""")
    op.execute("""
CREATE TRIGGER geo_data_sources_publication_guard
BEFORE INSERT OR UPDATE OF
    publication_eligible, verification_status, verified_at, verified_by,
    license_review_status, license_reviewed_at, license_reviewed_by,
    license_identifier, license_name, attribution_text
ON geo.data_sources
FOR EACH ROW EXECUTE FUNCTION geo.enforce_source_publication_eligibility()
""")

    op.execute("""
CREATE TABLE geo.source_evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES geo.data_sources(id) ON DELETE RESTRICT,
    evidence_type varchar(40) NOT NULL,
    evidence_uri text,
    evidence_checksum_sha256 char(64),
    captured_at timestamptz NOT NULL DEFAULT now(),
    captured_by uuid REFERENCES public.staff_users(id) ON DELETE RESTRICT,
    evidence_note text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_geo_source_evidence_type CHECK (
        evidence_type IN (
            'license_document', 'terms_of_use', 'provider_record',
            'collection_record', 'verification_record', 'field_record',
            'checksum_record', 'other'
        )
    ),
    CONSTRAINT ck_geo_source_evidence_sha256 CHECK (
        evidence_checksum_sha256 IS NULL
        OR evidence_checksum_sha256 ~ '^[0-9a-fA-F]{64}$'
    )
)
""")
    op.execute("""
CREATE INDEX ix_geo_source_evidence_source_time
ON geo.source_evidence(source_id, captured_at DESC)
""")
    op.execute("ALTER TABLE geo.source_evidence ENABLE ROW LEVEL SECURITY")
    op.execute("""
CREATE POLICY p_geo_source_evidence_tenant_isolation
ON geo.source_evidence
USING (EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = source_evidence.source_id
      AND ds.organization_id = geo.current_organization_id()
))
WITH CHECK (EXISTS (
    SELECT 1 FROM geo.data_sources ds
    WHERE ds.id = source_evidence.source_id
      AND ds.organization_id = geo.current_organization_id()
))
""")
    op.execute("""
CREATE OR REPLACE FUNCTION geo.reject_source_evidence_mutation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $geo_evidence$
BEGIN
    RAISE EXCEPTION 'geo.source_evidence is append-only';
END;
$geo_evidence$
""")
    op.execute("""
CREATE TRIGGER geo_source_evidence_append_only
BEFORE UPDATE OR DELETE ON geo.source_evidence
FOR EACH ROW EXECUTE FUNCTION geo.reject_source_evidence_mutation()
""")
    op.execute("""
GRANT SELECT, INSERT ON geo.source_evidence TO maalenex_geo_catalog_manager
""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS geo_source_evidence_append_only ON geo.source_evidence")
    op.execute("DROP FUNCTION IF EXISTS geo.reject_source_evidence_mutation()")
    op.execute("DROP POLICY IF EXISTS p_geo_source_evidence_tenant_isolation ON geo.source_evidence")
    op.execute("ALTER TABLE geo.source_evidence DISABLE ROW LEVEL SECURITY")
    op.execute("REVOKE ALL ON geo.source_evidence FROM maalenex_geo_catalog_manager")
    op.execute("DROP TABLE IF EXISTS geo.source_evidence")
    op.execute("DROP TRIGGER IF EXISTS geo_data_sources_publication_guard ON geo.data_sources")
    op.execute("DROP FUNCTION IF EXISTS geo.enforce_source_publication_eligibility()")
    op.execute("ALTER TABLE geo.data_sources DROP CONSTRAINT IF EXISTS ck_geo_source_license_review_evidence")
    op.execute("ALTER TABLE geo.data_sources DROP CONSTRAINT IF EXISTS ck_geo_source_license_review_status")
    op.execute("""
ALTER TABLE geo.data_sources
    DROP COLUMN IF EXISTS verification_notes,
    DROP COLUMN IF EXISTS evidence_reference,
    DROP COLUMN IF EXISTS source_method,
    DROP COLUMN IF EXISTS license_reviewed_by,
    DROP COLUMN IF EXISTS license_reviewed_at,
    DROP COLUMN IF EXISTS license_review_status
""")
