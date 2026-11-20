# MaaleNex — Independent Android/WebView Security Review Request v1.1

Repository: ake fadaka-git/maalenex
Pull request: #25 — https://github.com/akefadaka-git/maalenex/pull/25
Review target commit: c192a2439305e60a6cea0be75251b12d9a1939ec
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


## 7. Review target supersession and current evidence — v1.1 (2026-11-15)

This addendum supersedes the original v1.0 target commit and its earlier CI artifacts. The independent reviewer must use the exact current target below and must not substitute the older APK.

**Current exact review target:** `c192a2439305e60a6cea0be75251b12d9a1939ec`  
**Branch:** `feat/a3-passenger-only-integration`  
**PR:** [#25](https://github.com/akefadaka-git/maalenex/pull/25) — OPEN / DRAFT / UNMERGED  
**Base:** `main` at `78884c0f2609edbfc94a24e42d84824bff9eed20`

### Exact-head CI evidence

- Android shell verification [run #43719864854](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854) — PASS: dependency verification, SBOM generation/validation, trusted-navigation tests, APK assembly, Android lint and Android 15 emulator install/launch/WebView smoke.
- Full resolved-graph OSV scan (job `132830678963`) — PASS; scanner output: **No issues found**.
- OSV PR-diff scan [run #43719864941](https://github.com/akefadaka-git/maalenex/actions/runs/43719864941) — PASS; frontend lockfile scan completed with no issues.
- Brand assets and frontend verification [run #43719864840](https://github.com/akefadaka-git/maalenex/actions/runs/43719864840) — PASS.
- Cloudflare Pages build [run #43719864735](https://github.com/akefadaka-git/maalenex/actions/runs/43719864735) — PASS; deployment steps skipped/not executed.

### Exact APK identity

- Artifact: [debug APK](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163739417)
- File: `app-debug.apk`
- Size: 2,643,438 bytes
- SHA-256: `ca6e2bb1617d6585cf3cdabd457821bbe8b1f1f9933740f3203b07dedc1d1b54`

This is a debug APK, not a production/release-signed package. The reviewer must verify the downloaded APK hash before testing.

### Additional evidence artifacts

- [Resolved CycloneDX SBOMs and frontend lockfile](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164665214)
- [Gradle SHA-256 verification metadata](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163599898)
- [OSV SARIF — zero results](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163992272)
- [Android lint report](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164391194)
- [Trusted-navigation unit tests](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164580548)
- [WebView emulator smoke evidence](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164391345)

The SBOM scan covered 27 runtime, 29 test, 19 compile, 112 build-tool and 160 frontend package instances. No known OSV issues matched the scanned inputs. This does not replace manual dependency review, dynamic security testing or independent sign-off.

### New/updated files in the review scope

- `android/build.gradle.kts` — patched build-tool dependency pins, including KGP 2.4.21.
- `android/gradle/verification-metadata.xml` — committed Gradle SHA-256 integrity metadata.
- `.github/scripts/gradle-report-to-cyclonedx.py` — generates SBOMs from selected Gradle versions.
- `.github/scripts/verify-gradle-sbom.py` — validates SBOM structure and remediation pins.
- `.github/workflows/android-shell-verification.yml` — exact-head build, SBOM validation, OSV input and emulator evidence workflow.
- `.github/workflows/osv-scanner.yml` — frontend PR-diff lockfile scan; Android dependencies are scanned from the Android workflow's resolved SBOMs.
- `docs/security/PRELIMINARY-DEPENDENCY-SUPPLY-CHAIN-REVIEW-v1.0.md` — v1.2 dependency triage and scan disposition.

### Residual platform/toolchain note

KGP 2.4.21 is documented as fully supported through Gradle 9.7.0; this project uses Gradle 9.9.1 to retain its security fixes. The exact build passed on the review target, but the documented full-support matrix does not yet cover Gradle 9.9.1. Please include this compatibility caveat in the residual-risk assessment.

No independent reviewer has yet completed or signed this assessment. Independent security review remains MISSING. TalkBack remains deferred by Owner; external-keyboard testing is not available. The Samsung Galaxy A16 / Android 16 device checks remain Owner-reported evidence as listed in section 5.
