# MaaleNex Android shell

## Application contract

- Application ID / namespace: `com.maalenex.moto` (legacy package identifier retained pending a separately reviewed migration)
- Display name: MaaleNex
- Minimum SDK: API 23; compile/target SDK: API 35
- JDK: 17; Android Gradle Plugin: 8.7.3; Gradle: 8.9; Kotlin: 2.0.21

The native Kotlin activity hosts the passenger-only React/Vite guest preview using AndroidX WebKit's `WebViewAssetLoader`. The web bundle is copied into the APK as local assets. The activity exposes no JavaScript bridge, disables file/content access, blocks navigation outside the packaged asset origin, and does not request network access.

## Build

Build the frontend before packaging:

```sh
cd frontend
npm install
npm test
npm run build
cd ../android
gradle --no-daemon :app:testDebugUnitTest :app:assembleDebug :app:lintDebug
```

## Launcher resources

API 23–25 use vector drawable fallbacks. API 26+ uses adaptive foreground/background layers; API 33+ includes a monochrome themed-icon layer. Physical-device launcher-mask acceptance remains separate.

## Product and security boundary

The packaged UI is a public passenger-only guest preview. It contains no sign-in, registration, passenger data collection, booking, payment, ticketing, driver/cargo/fleet workspace, or public administration. No privileged JavaScript bridge or production API connectivity is included. Android build/emulator success does not establish physical-device, accessibility, security-review, or production readiness.
