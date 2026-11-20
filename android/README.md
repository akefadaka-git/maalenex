# MaaleNex Android application

## Application contract

- Application ID / namespace: `com.maalenex.moto` (legacy package identifier retained pending a separately reviewed migration)
- Display name: MaaleNex
- Minimum SDK: API 23; compile/target SDK: API 35
- JDK: 17

The native Kotlin activity hosts the Amharic-first React/Vite application through AndroidX WebKit's `WebViewAssetLoader`. The web bundle is packaged as local assets. The activity exposes no JavaScript bridge, disables file/content access, blocks navigation outside the packaged asset origin, and does not enable external network access.

## Branded startup

The Android 12+ system splash resources use the MaaleNex emblem. A native, locally rendered splash overlay then remains visible until the packaged web application renders meaningful root content, with a bounded timeout and error fallback. This avoids removing the brand screen while the WebView is still blank or loading. Launcher adaptive foreground, monochrome icon, and background use the same MaaleNex identity.

Physical-device splash and launcher appearance still require verification on supported Android versions and OEM launcher behavior.

## Build

Build the frontend before packaging:
```sh
cd frontend
npm ci
npm test
npm run typecheck
npm run build
cd ../android
gradle --no-daemon :app:testDebugUnitTest :app:assembleDebug :app:lintDebug
```

## Current product boundary

The packaged UI contains the full platform screen foundation: dashboard, map preview, wallet, profile, login, registration, Help, Report, and About. Passenger authentication, persistent profile storage, live map provider connectivity, wallet API integration, payment-provider connectivity, and real-money movement are not yet enabled. The wallet ledger is an internal backend accounting foundation only.

No privileged JavaScript bridge, production API connectivity, or live financial operation is included. Android build/emulator success does not establish physical-device, accessibility, independent security-review, or production readiness.
