# MAALENEX-IA-A3.8 — Geographic Provenance and Licensing

**Disposition:** IMPLEMENTED — CI VERIFICATION PENDING  
**Repository:** `akefadaka-git/maalenex`  
**Branch:** `feat/a3-canonical-postgis-integration`  
**Migration:** `0024_geo_provenance_licensing`  
**Parent:** `0023_geo_tenant_rls_permissions`

## 1. Purpose

Separate geographic correctness/verification from legal permission to reuse or publish a dataset. A geometrically verified source is not automatically licensed for public distribution.

## 2. Source provenance

The canonical `geo.data_sources` record retains provider, source name/URI/version/checksum, license identifier/name/URI, attribution, source CRS, collection and verification timestamps, verifier, responsible actor and publication eligibility. A3.8 adds:
- source collection method and evidence reference;
- verification notes;
- independent license-review status, reviewer and timestamp.

License review states are `pending`, `approved`, `denied`, and `restricted`. Approval requires a reviewer identity and timestamp. A source cannot be publication-eligible unless it is verified, has a verifier and verification timestamp, has an approved license review, and has non-empty license and attribution fields.

## 3. Evidence register

`geo.source_evidence` stores append-only evidence references for license documents, terms of use, provider records, collection records, verification records, field records and checksums. Evidence can be linked to a URI or represented by a SHA-256 checksum and controlled note. Evidence rows inherit tenant visibility through their source record and are protected by RLS. Catalog manager receives SELECT/INSERT only; UPDATE/DELETE are rejected.

## 4. Fail-closed migration treatment

The migration does not infer license status from existing records. Any pre-existing source marked publication-eligible is made ineligible and moved to `pending` license review. This is a deliberate fail-closed safety change. Existing source rows and geometries are retained. Re-publication requires a documented review and an explicit authorized update.

No authoritative Maale Woreda boundary, road-network source, or external license has been added. Those remain unresolved pending documentary source evidence and owner-approved acquisition/publication decisions. Synthetic CI fixtures use explicitly synthetic terms and are not production data.

## 5. Verification requirements

- [ ] Upgrade/downgrade/re-upgrade on disposable PostGIS.
- [ ] Verify missing license approval blocks publication eligibility.
- [ ] Verify tenant-scoped source evidence and append-only enforcement.
- [ ] Verify malformed SHA-256 evidence is rejected.
- [ ] Re-run A3.7 public leakage and actual Martin tile tests after the new publication gate.
- [ ] Repository-wide Alembic metadata parity remains separately tracked; no waiver or suppression.

No production database was accessed or changed. No merge or deployment is authorized by this package.
