"""General platform accounts and auditable trust-verification records.

This domain is separate from staff authentication. Secret material and identity
documents are never stored in plaintext: identifiers contain ciphertext plus a
keyed lookup digest; credentials contain password/public-key verifiers only.
"""
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Index, LargeBinary, String,
    UniqueConstraint, Uuid, func, text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"
    __table_args__ = (CheckConstraint(
        "status IN ('pending', 'active', 'suspended', 'closed')",
        name="ck_platform_accounts_status",
    ),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    preferred_locale: Mapped[str] = mapped_column(String(16), nullable=False, default="am-ET")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccountIdentifier(Base):
    __tablename__ = "account_identifiers"
    __table_args__ = (
        CheckConstraint("identifier_type IN ('email', 'phone')", name="ck_account_identifier_type"),
        Index(
            "uq_active_account_identifier_digest", "identifier_type", "lookup_digest",
            unique=True, postgresql_where=text("revoked_at IS NULL"),
        ),
        Index("ix_account_identifiers_account_id", "account_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False
    )
    identifier_type: Mapped[str] = mapped_column(String(16), nullable=False)
    lookup_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    encrypted_value: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccountCredential(Base):
    __tablename__ = "account_credentials"
    __table_args__ = (
        CheckConstraint("credential_type IN ('password', 'passkey')", name="ck_account_credential_type"),
        CheckConstraint("status IN ('active', 'revoked')", name="ck_account_credential_status"),
        Index("ix_account_credentials_account_id", "account_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False
    )
    credential_type: Mapped[str] = mapped_column(String(24), nullable=False)
    verifier: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccountServiceRoleAssignment(Base):
    __tablename__ = "account_service_role_assignments"
    __table_args__ = (
        Index(
            "uq_active_account_service_role", "account_id", "organization_id",
            "service_code", "role_id", unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
        Index("ix_account_service_roles_org_service", "organization_id", "service_code"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    service_code: Mapped[str] = mapped_column(
        String(32), ForeignKey("platform_services.code", ondelete="RESTRICT"), nullable=False
    )
    role_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("access_roles.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TrustVerificationCase(Base):
    __tablename__ = "trust_verification_cases"
    __table_args__ = (
        CheckConstraint(
            "(subject_type = 'individual' AND account_id IS NOT NULL AND organization_id IS NULL) "
            "OR (subject_type = 'organization' AND organization_id IS NOT NULL AND account_id IS NULL)",
            name="ck_trust_case_exactly_one_subject",
        ),
        CheckConstraint("subject_type IN ('individual', 'organization')", name="ck_trust_case_subject_type"),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'in_review', 'approved', 'rejected', 'expired', 'revoked')",
            name="ck_trust_case_status",
        ),
        Index(
            "uq_open_individual_trust_case", "account_id", unique=True,
            postgresql_where=text(
                "account_id IS NOT NULL AND status IN ('submitted', 'in_review')"
            ),
        ),
        Index(
            "uq_open_organization_trust_case", "organization_id", unique=True,
            postgresql_where=text(
                "organization_id IS NOT NULL AND status IN ('submitted', 'in_review')"
            ),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    subject_type: Mapped[str] = mapped_column(String(20), nullable=False)
    account_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=True
    )
    organization_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    verification_level: Mapped[str] = mapped_column(String(32), nullable=False, default="basic")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="draft")
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TrustEvidence(Base):
    __tablename__ = "trust_evidence"
    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted', 'accepted', 'rejected', 'expired')",
            name="ck_trust_evidence_status",
        ),
        Index("ix_trust_evidence_case_id", "case_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("trust_verification_cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_type: Mapped[str] = mapped_column(String(48), nullable=False)
    issuer_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    document_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    private_object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    media_type: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="submitted")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TrustReviewEvent(Base):
    __tablename__ = "trust_review_events"
    __table_args__ = (
        UniqueConstraint("case_id", "sequence_number", name="uq_trust_review_case_sequence"),
        Index("ix_trust_review_events_case_id", "case_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("trust_verification_cases.id", ondelete="RESTRICT"),
        nullable=False,
    )
    sequence_number: Mapped[int] = mapped_column(nullable=False)
    actor_staff_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("staff_users.id", ondelete="RESTRICT"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    from_status: Mapped[str] = mapped_column(String(24), nullable=False)
    to_status: Mapped[str] = mapped_column(String(24), nullable=False)
    reason_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccountSession(Base):
    __tablename__ = "account_sessions"
    __table_args__ = (
        Index("ix_account_sessions_account_id", "account_id"),
        Index("ix_account_sessions_expires_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False
    )
    secret_digest: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    csrf_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AccountChallenge(Base):
    __tablename__ = "account_challenges"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ('identifier_verification', 'password_recovery')",
            name="ck_account_challenge_purpose",
        ),
        Index("ix_account_challenges_account_id", "account_id"),
        Index("ix_account_challenges_expires_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False
    )
    identifier_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("account_identifiers.id", ondelete="CASCADE"), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    token_digest: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccountLoginAttempt(Base):
    __tablename__ = "account_login_attempts"

    key_digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    failed_count: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
