# MaaleNex Moto Android shell

## Application contract

- Application ID: `com.maalenex.moto`
- Namespace: `com.maalenex.moto`
- Minimum SDK: API 23 (Android 6.0)
- Compile / target SDK: API 35
- JDK: 17
- Android Gradle Plugin: 8.7.3
- Gradle: 8.9
- Kotlin: 2.0.21

The native Kotlin activity hosts the React/Vite application using AndroidX WebKit's `WebViewAssetLoader`. The web bundle is copied into the APK as local assets; the activity does not expose a JavaScript bridge, does not enable file URL access, blocks navigation outside the packaged asset origin, and does not request network access.

## Build

Build the frontend first so Gradle can package its output:

```sh
cd frontend
npm install
npm test
npm run build

cd ../android
gradle --no-daemon :app:assembleDebug :app:lintDebug
```

Use JDK 17, Gradle 8.9 and Android SDK platform 35. CI installs these tools and runs the same build plus an Android 15 emulator launch check.

## Launcher resources

- API 23–25: `mipmap-anydpi/ic_launcher.xml` and `ic_launcher_round.xml` provide vector drawable fallbacks.
- API 26+: `mipmap-anydpi-v26/` provides adaptive foreground/background layers.
- API 33+: adaptive resources include the monochrome themed-icon layer.

The minimum SDK is 23, where vector drawables are supported. Density-specific PNG launcher fallbacks are therefore not required for this SDK range. If the minimum SDK is ever lowered below API 21, add raster fallback assets and revise this decision.

## Acceptance boundaries

CI emulator acceptance proves that the debug APK assembles, installs and launches with the packaged web UI on an API 35 emulator. It does not prove behavior on a physical device, OEM launcher mask appearance, accessibility conformance, production API connectivity, authentication, payments, or commercial readiness. Physical-device acceptance remains a separately recorded gate.

All current role workspace interactions use synthetic sample data and local preview state. They do not create real bookings, dispatch trips, alter server-side availability, approve users, or perform fleet administration.
