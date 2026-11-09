# Android device acceptance remediation

## Scope and source baseline
This remediation is based on PR #5's exact source head `563bd5c9eba6e69c1de08a29f00b113679c19cc5`. It is isolated on `fix/android-device-acceptance-emulator`; no merge or deployment is included.

## Navigation
- Touch-sized in-app Home / Find trips / Help anchors replace the root URL navigation.
- Navigation targets and the bilingual Help destination are covered by frontend DOM tests.
- Online/offline transitions are exposed as an accessible status message.
- The offline indicator does not imply offline booking or synchronization.

## API-origin handling
- Every frontend API request is routed through `apiFetch`; the QR image uses the same validated API origin.
- `VITE_API_BASE_URL` must be an absolute HTTPS origin, without credentials, path, query or fragment. HTTP is accepted only for localhost development.
- Placeholder origins are rejected at build/runtime rather than silently treated as a real API.
- API requests include credentials for the backend's booking-access cookie flow.
- A blank origin deliberately retains same-origin behavior for local development. It is not a valid installed-app API configuration.

## Native WebView CSRF compatibility
- The booking verification response now returns the non-secret CSRF token so the Capacitor WebView can retain it in session storage and send it in `X-CSRF-Token`.
- For HTTPS requests, booking access and CSRF cookies use `SameSite=None; Secure`; local HTTP development retains `SameSite=Lax`.
- The test API must explicitly allow the installed app origin (including the Capacitor origin) in `CORS_ORIGINS`, with credentials enabled. Do not use wildcard CORS with credentials.
- Cookie persistence and CSRF behavior must still be verified on the target Android WebView against the actual HTTPS test API. SameSite configuration alone is not proof that the device accepts the cookie.

## Reproducible CI acceptance
The workflow runs frontend tests and typecheck/build, creates a debug APK, starts an API 35 Android emulator with bounded boot readiness, installs the APK, launches `com.maalenex.moto`, verifies the app is foregrounded, checks for Android fatal exceptions, and stores the UI hierarchy plus screenshot as CI artifacts.

This is an emulator install/launch smoke test. It does not substitute for physical-device acceptance or a live API journey.

## Blocking dependencies for full acceptance
1. Configure `MAALENEX_TEST_API_BASE_URL` to the actual authorized HTTPS test API origin. No guessed or placeholder host is permitted.
2. The current G1 backend configuration still restricts its database to local development/test PostgreSQL and only permits `development` / `test` app environments. A separately hosted test API requires a separately approved, safe deployment configuration and database.
3. The test API must publish at least two synthetic locations and matching synthetic trips.
4. Verify CORS, cookie persistence, CSRF mutation, booking retrieval, QR fetch and support-case retrieval on the Android WebView.
5. Install and repeat the same smoke and journey checks on a physical Android device; record device model, Android version, APK SHA-256, API origin, test data IDs, timestamps and outcomes.

## Safety boundary
Synthetic data only. No production passenger records, payment collection, travel-ticket issuance, boarding authorization, commercial activation, merge, signing or deployment is authorized by this change.
