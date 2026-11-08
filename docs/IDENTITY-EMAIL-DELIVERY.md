# MaaleNex account email delivery

## Scope

The account identity service uses a provider-neutral SMTP adapter for three email challenges:

- email identifier verification;
- credential enrollment after identifier verification;
- password recovery.

The adapter uses Python's standard library. It does not require a vendor SDK, a paid API, a subscription, a deposit or a billing/top-up action. An SMTP endpoint and permission to send from the configured address are still required before real delivery can occur.

SMS is intentionally not activated in this increment. The SMS adapter contract is defined so a provider can be added later without changing account lifecycle logic. Phone-number registrations therefore report unsupported_channel until an SMS adapter is authorized and configured.

## Configuration

Start from backend/.env.example. Keep IDENTITY_EMAIL_DELIVERY_ENABLED=false until a working SMTP endpoint and authorized sender address are available.

For an SMTP submission server using STARTTLS (commonly port 587):

    IDENTITY_EMAIL_DELIVERY_ENABLED=true
    IDENTITY_SMTP_HOST=smtp.example.org
    IDENTITY_SMTP_PORT=587
    IDENTITY_SMTP_USERNAME=your-smtp-user
    IDENTITY_SMTP_PASSWORD=inject-from-secret-store
    IDENTITY_SMTP_FROM_EMAIL=no-reply@example.org
    IDENTITY_SMTP_FROM_NAME=MaaleNex
    IDENTITY_SMTP_STARTTLS=true
    IDENTITY_SMTP_USE_SSL=false
    IDENTITY_SMTP_TIMEOUT_SECONDS=10

For implicit TLS (commonly port 465), set IDENTITY_SMTP_PORT=465, IDENTITY_SMTP_STARTTLS=false and IDENTITY_SMTP_USE_SSL=true. Do not enable STARTTLS and implicit SSL together.

SMTP username/password are optional only when the authorized SMTP relay permits authenticated-network or other approved unauthenticated submission. Never weaken transport security to work around a provider configuration problem.

## Secret handling

- Local development: use an untracked backend/.env file.
- GitHub Actions: add credentials as repository or environment Actions Secrets only if a workflow genuinely needs to send a controlled test email. Never put SMTP credentials in source files, workflow YAML, fixtures, PR text or logs.
- A deployment environment must receive the same settings through its secret manager or protected environment variables.
- Do not reuse identity encryption/lookup keys as SMTP credentials.
- Do not enable IDENTITY_EXPOSE_TEST_TOKENS for any environment that sends real messages.

## Delivery behavior

- Challenge rows are committed before SMTP delivery is attempted.
- Tokens are stored as digests in the database; the raw token is passed only to the delivery adapter.
- Registration and identifier verification responses report sent, failed, not_configured or unsupported_channel.
- Recovery always returns a generic accepted response so the API does not reveal whether an account exists. Delivery failures must be investigated through protected operational telemetry, never by logging challenge tokens or full email content.
- Challenge expiry is 15 minutes for identifier verification and 30 minutes for credential enrollment and recovery.
- A successful SMTP submission means the relay accepted the message; it does not prove final inbox delivery.

## Verification and operational boundary

Synthetic tests use a fake SMTP transport and never contact an external mail server. A real end-to-end delivery test requires an explicitly authorized sender and recipient, a configured SMTP endpoint, and a controlled test account.

This repository's current G1 guardrails still enforce development/test mode and synthetic-only data. SMTP support does not authorize production operation, merge, deployment or live customer onboarding.


## Challenge resend and abuse controls

The authenticated account-independent resend endpoint is:

    POST /api/v1/identity/challenges/resend

Request fields are identifier_type (email or phone), identifier_value, and purpose (identifier_verification, credential_enrollment or password_recovery). The endpoint returns the same generic accepted message for eligible, unknown and throttled accounts to reduce account enumeration.

Resend controls are persisted in PostgreSQL using a keyed digest of the identifier digest, purpose and client IP; raw identifiers and IP addresses are not stored in the throttle key table:

- 60-second cooldown per identifier/purpose/client-IP combination;
- maximum five issued resend challenges in a rolling one-hour window;
- one-hour lock after the hourly limit is reached;
- each accepted resend invalidates outstanding challenges of the same purpose and issues a fresh expiring token;
- no raw challenge value is written to logs.

These controls are server-side and survive process restarts. They do not replace edge/WAF-level IP rate limiting, provider-side sending limits, monitoring or CAPTCHA/risk controls if abuse patterns warrant them.

## Non-sending SMTP connectivity test

A manual GitHub Actions workflow is provided at .github/workflows/identity-smtp-connectivity.yml. It checks SMTP TCP connectivity, TLS negotiation and configured authentication only. It does not send an email and does not require a synthetic recipient mailbox.

To use it, configure the following GitHub Actions secrets: MAALENEX_SMTP_HOST and MAALENEX_SMTP_FROM_EMAIL; optionally MAALENEX_SMTP_PORT, MAALENEX_SMTP_USERNAME, MAALENEX_SMTP_PASSWORD, MAALENEX_SMTP_STARTTLS and MAALENEX_SMTP_USE_SSL. Then manually dispatch the workflow with confirm_check=true. Missing secrets cause a safe failure before attempting a connection. Secret values are not printed.

A successful connection check proves transport/TLS/authentication only. It does not prove message acceptance or inbox delivery. A real message test must be a separate, explicitly authorized test to a controlled mailbox.
