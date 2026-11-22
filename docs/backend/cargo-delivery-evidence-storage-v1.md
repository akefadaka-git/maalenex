# MaaleNex Cargo Delivery Evidence Storage v1

## Scope

Backend-only private evidence upload and verification for cargo delivery proof. This increment extends the existing S3-compatible private object-storage implementation; it does not change the approved provider, endpoint policy, bucket configuration, or fleet-compliance behavior.

## Upload contract

- `POST /api/v1/cargo/dispatches/{dispatch_id}/delivery-proof/upload-intents`
- Requires the assigned carrier's `operator.cargo.delivery_proof.submit` permission, CSRF protection, and an `in_transit` dispatch.
- Accepts PDF, JPEG, or PNG with a declared content length from 1 byte through 10 MiB.
- Returns a five-minute presigned PUT intent. The private object key is scoped to `cargo-delivery/{carrier_organization_id}/{dispatch_id}/`.
- The API does not accept a public URL or arbitrary object path as evidence.

## Verification and proof submission

- `POST /api/v1/cargo/dispatches/{dispatch_id}/delivery-proof` verifies that the supplied private object key belongs to the exact carrier and dispatch.
- Verification checks object existence, size, declared media type, and the file signature before the proof record is persisted.
- Evidence bytes remain in private object storage; only the private object key is stored as `evidence_reference`.
- Storage-not-configured failures return 503; invalid, missing, cross-dispatch, or mismatched evidence returns 422.
- Upload-intent creation is audited without logging the presigned URL or credentials.

## Security and boundaries

- Existing Cloudflare R2 production endpoint validation and local S3-compatible test endpoint restrictions remain unchanged.
- No public download URL, public bucket, client-side evidence handling, frontend, provider migration, retention-policy change, or production activation is introduced.
- CI uses synthetic fixtures and ephemeral local S3-compatible storage only.
