# MaaleNex Android debug APK

## Build and verification

The MaaleNex Android Debug APK workflow builds the React/Vite frontend, runs frontend tests, packages the web assets in a Capacitor Android WebView, and assembles a debug APK. It uses Node.js 22, Java 17 and pinned Capacitor 6.2.1 packages. The Android project is generated in the GitHub Actions runner; generated Gradle files and SDK output are not committed.

A successful workflow uploads the APK as the `maalenex-android-debug` artifact for 14 days. This is a debug build for controlled installation and UI testing, not a signed release.

## API origin

The build reads the optional GitHub Actions repository variable `MAALENEX_TEST_API_BASE_URL` into the frontend build variable `VITE_API_BASE_URL`.

- Set it only to an approved HTTPS test API origin, without a path, credentials, query or fragment.
- Do not put API keys, passwords, tokens or other secrets in this variable.
- If it is unset, the APK is a UI preview. Same-origin API calls cannot reach a separately hosted FastAPI service from the standalone WebView.
- If it is set, the remote test API must separately permit the app origin and support the required credentialed CORS, secure cookie and CSRF behavior. Those cross-origin controls must be tested end-to-end before calling the Android passenger workflow functional.

## Install and smoke test

Download the APK from the successful workflow run's Artifacts section, transfer it to an Android test device, allow installation from the chosen file source if Android asks, and install it. Verify:
- application installation and launch;
- Amharic-first rendering and English language switch;
- About page, creator contact links and external social links;
- responsive layout, text scaling, rotation, zoom and keyboard/focus behavior;
- when an approved test API origin is configured, location loading, trip search, seat availability, synthetic booking hold, contact challenge, reservation recovery and support requests.

Record device model, Android version, build SHA, APK SHA-256 and each result. Do not enter real passenger data.

## Runtime and safety boundaries

- The APK contains frontend web assets only. It does not bundle FastAPI, PostgreSQL, operator services or a production backend.
- Synthetic-data-only development remains enforced.
- No real passenger bookings, payment collection, travel-ticket issuance or boarding authority are enabled.
- A debug APK is not a Play Store release. Release signing, application ID ownership checks, privacy/legal review, independent security review and deployment approval remain separate gates.
- Do not distribute this debug APK as a live passenger application.
