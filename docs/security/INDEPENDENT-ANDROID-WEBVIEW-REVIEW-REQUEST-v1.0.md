# MaaleNex — Independent Android/WebView Security Review Request v1.0

Repository: ake fadaka-git/maalenex
Pull request: #25 — https://github.com/akefadaka-git/maalenex/pull/25
Review target commit: e2dd491757a919b87a5f26478982f758493ecb6f
Review branch: feat/a3-passenger-only-integration
Requested review: Independent assessment by a reviewer who did not implement this change.

## 1. Purpose and boundaries

Assess the Android application shell and packaged React/Vite application before any production or deployment decision. This request is not authorization to merge, deploy, publish a release, activate live services, collect real passenger data, enable payments, or onboard real operators.

The current app is a public, passenger-only development preview. It has no real account/authentication flow, backend connectivity, booking, ticketing, payment, driver, cargo, fleet, or administrative workspace.

## 2. Review target and evidence

Review the exact commit above, not a moving branch head. Confirm the commit SHA before starting and record the actual reviewed SHA in the report.

Relevant files:
- android/app/src/main/AndroidManifest.xml
- android/app/src/main/java/com/maalenex/moto/MainActivity.kt
- android/app/src/main/java/com/maalenex/moto/TrustedNavigationPolicy.kt
- android/app/src/test/java/com/maalenex/moto/TrustedNavigationPolicyTest.kt
- android/app/build.gradle.kts
- frontend/index.html
- frontend/vite.config.ts
- .github/scripts/verify-android-web-csp.py

Exact-head automated evidence:
- Brand/frontend workflow #69: https://github.com/akefadaka-git/maalenex/actions/runs/43699256646
- Cloudflare Pages build #86: https://github.com/akefadaka-git/maalenex/actions/runs/43699256656 (build only; deployment steps skipped)
- Android shell workflow #59: https://github.com/akefadaka-git/maalenex/actions/runs/43699256694
- Debug APK: https://github.com/akefadaka-git/maalenex/actions/runs/43699256694/artifacts/14154699840
- WebView smoke evidence: https://github.com/akefadaka-git/maalenex/actions/runs/43699256694/artifacts/14155887104
- Trusted-navigation tests: https://github.com/akefadaka-git/maalenex/actions/runs/43699256694/artifacts/14154894687
- Android lint: https://github.com/akefadaka-git/maalenex/actions/runs/43699256694/artifacts/14154984695

Artifacts are temporary and may expire. If expired, reproduce from the exact reviewed commit; do not silently substitute a newer APK.

## 3. Required independent review checks

### A. WebView boundary and navigation
- Verify the only permitted top-level document is the exact packaged HTTPS entry document.
- Test redirects, external URLs, subframes, intent:, javascript:, file:, content:, custom schemes, malformed URLs, userinfo, host lookalikes, unusual ports, encoded traversal, duplicate separators, backslashes, query strings, and fragments.
- Verify subresource loading is constrained to packaged assets and no external navigation can escape the app boundary.
- Inspect WebView settings, debugging state, safe browsing behavior, renderer failure handling, and lifecycle behavior.
- Confirm no JavaScript interface, bridge, message channel, or native plugin is exposed.

### B. Android platform and packaged assets
- Inspect manifest permissions, exported components, backup/data-extraction rules, cleartext policy, network security configuration, deep links, intent filters, and target/min SDK implications.
- Verify packaged asset integrity, asset-loader path mapping, relative resource URLs, and behavior on supported Android API levels.
- Inspect release/debug build differences, signing assumptions, shrinker rules, and whether debug-only functionality can enter a release build.
- Assess whether device logs disclose sensitive data. The current preview should not process real user or passenger data.

### C. Content Security Policy and frontend
- Independently parse the built APK's actual index.html and verify the effective CSP.
- Test duplicate/invalid directives, inline script/style injection, object/frame/base/form restrictions, worker and connect sources, and CSP bypass assumptions.
- Inspect DOM XSS sinks, unsafe HTML usage, URL handling, external resource loading, and dependency/runtime supply-chain risks.
- Confirm no credentials, secrets, personal-data collection, or unintended backend endpoints are present in the public guest preview.

### D. Dependencies and supply chain
- Review Android Gradle dependencies and plugin versions, React/Vite/npm dependencies, lockfiles, transitive dependencies, known advisories, provenance/integrity, and update posture.
- Run appropriate dependency vulnerability and malware checks against the exact commit and APK.
- Record tool names, database/advisory snapshot date, exact versions, and findings. A scan with no findings is not proof of absence of vulnerabilities.

### E. Dynamic testing
- Install the exact APK on a test device/emulator and exercise navigation attacks, offline behavior, malformed asset requests, rotation, process recreation, and app lifecycle.
- Use a proxy/network monitor to verify that the app makes no unexpected network requests; distinguish Android system traffic from app traffic.
- Test backup/restore and data extraction behavior where applicable.
- Record device/API level, APK SHA-256, test steps, observed results, and sanitized logs.

## 4. Finding severity and report format

Classify findings as Critical, High, Medium, Low, or Informational. For each finding provide:
- Unique ID and severity.
- Affected file/component and exact commit.
- Preconditions and reproducible steps.
- Security impact and realistic attack scenario.
- Evidence (sanitized logs, screenshots, test output, or code references).
- Recommended remediation and retest result.

The final report must include:
1. Reviewer identity/organization and independence statement.
2. Exact commit SHA and APK SHA-256 reviewed.
3. Scope, exclusions, tools and versions.
4. Test coverage and limitations.
5. Findings table with severity and remediation status.
6. Explicit residual-risk statement.
7. Overall verdict: PASS, PASS WITH FINDINGS, or FAIL.
8. Reviewer date and sign-off.

## 5. Current known limitations to preserve

- Internal source/configuration review and exact-head CI have passed; neither is an independent security assessment.
- Keyboard navigation has not been physically tested because no external keyboard is available.
- TalkBack is deferred by Owner for this acceptance pass.
- Owner-reported Samsung Galaxy A16 / Android 16 checks: installation/launch, Amharic/English display, pinch zoom, system font scaling, rotation, and increased display-size layout are PASS.
- Zoom resets after complete app termination/relaunch; zoom remains after ordinary reopen.
- No production activation, deployment, merge, or real-data processing is authorized.

## 6. Reviewer response

Please return the completed report as a signed PDF or Markdown document and attach/link the evidence. Do not change the reviewed branch or deploy the application as part of this assessment. Any proposed code remediation must be submitted separately for Owner review.
