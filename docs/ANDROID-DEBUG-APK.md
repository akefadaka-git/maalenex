# MaaleNex Moto Android Debug APK

## Build

The `Android Debug APK` GitHub Actions workflow builds the React/Vite frontend and packages its production assets in a Capacitor Android WebView. It uses Node.js 20, Java 17 and pinned Capacitor 6.2.1 packages. The Android project is generated in the runner, so generated Gradle files and SDK output are not committed to the application source branch.

The workflow uploads `app-debug.apk` as the `maalenex-moto-android-debug` artifact for 14 days. This is a debug build for installation and UI smoke testing, not a signed release.

## Install and test

Download the APK from the successful workflow run's Artifacts section, transfer it to an Android test device, allow installation from the chosen file source if Android asks, and install it. Verify that the app opens, renders the Amharic-first passenger interface, switches to English, and handles navigation without crashing.

## Runtime and safety boundaries

- The APK contains the frontend web assets only. It does not bundle FastAPI, PostgreSQL, operator services or a production backend.
- The current frontend uses same-origin `/api` requests. In the standalone Capacitor WebView those requests do not reach the separately hosted FastAPI service unless a future approved API-origin configuration or secure backend deployment is provided.
- No production API endpoint, credentials, live passenger data, payment integration, ticket issuance or boarding authority is configured by this build.
- Synthetic-only development/test restrictions remain in force.
- A debug APK is not a Play Store release. Release signing, application ID ownership checks, privacy/legal review, device compatibility testing and deployment approval remain separate gates.
- Do not distribute this debug APK as a live passenger application.

## Verification evidence

A successful workflow verifies that the web assets compile and Android Gradle produces a non-empty debug APK for the exact workflow commit. It does not replace installation/launch testing on a physical Android device or emulator.
