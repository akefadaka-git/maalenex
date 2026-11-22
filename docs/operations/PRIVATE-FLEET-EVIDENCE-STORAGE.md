# Private fleet-compliance object storage

Cloudflare R2 is the approved target provider, but live activation remains disabled.
Storage is disabled by default and only runs in the existing synthetic development/test environment.

## Runtime configuration

Set these variables only in a local development/test runtime:

- `OBJECT_STORAGE_ENABLED=true`
- `OBJECT_STORAGE_PROVIDER=r2`
- `OBJECT_STORAGE_ENDPOINT_URL=http://127.0.0.1:9000` for a local S3-compatible test service, or the account's Cloudflare R2 S3 endpoint when separately authorized
- `OBJECT_STORAGE_BUCKET=<private-test-bucket>`
- `OBJECT_STORAGE_ACCESS_KEY_ID=<scoped-test-key>`
- `OBJECT_STORAGE_SECRET_ACCESS_KEY=<test-secret>`

Never commit credentials, expose them to the frontend, or use a public bucket.
The endpoint must be a Cloudflare `*.r2.cloudflarestorage.com` HTTPS endpoint;
the only HTTP exception is localhost for local tests. This PR creates no bucket,
credentials, production endpoint or paid service.

## Upload lifecycle

1. Organization-scoped `operator.fleet.manage` staff request an upload intent.
2. The API returns a random vehicle-scoped key and five-minute content-type-bound
   presigned PUT URL.
3. The client uploads directly to the private bucket. The URL is a bearer token;
   never log or persist it.
4. The API verifies the exact organization/vehicle key prefix, object existence,
   byte length, declared media type and file signature before creating a pending
   compliance-review record.
5. Platform fleet reviewers retain the separate approval/rejection workflow.
   Storage verification does not approve a document.

Only PDF, JPEG and PNG files up to 10 MiB are accepted. The current G1 data
classification remains synthetic-only. Real identity, registration, insurance,
permit or other sensitive records must not be uploaded until classification,
retention, access, malware-scanning/quarantine and data-protection controls are
separately approved. Malware scanning is not implemented and remains a
pre-production requirement.

The implementation uses the S3 API abstraction. Local S3-compatible storage is
the CI/test target. R2 is not contacted unless a runtime explicitly enables it
and supplies credentials. No live R2 credentials or paid activation are included.
