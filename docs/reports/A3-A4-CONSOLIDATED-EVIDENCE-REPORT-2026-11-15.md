# MaaleNex — A3/A4 Consolidated Implementation and Verification Evidence Report

**Report date:** 2026-11-15  
**Repository:** `akefadaka-git/maalenex`  
**Implementation branch:** `feat/a3-passenger-only-integration`  
**Pull request:** [#25 — A3 passenger-only integration](https://github.com/akefadaka-git/maalenex/pull/25)  
**Verified code/workflow head:** `c192a2439305e60a6cea0be75251b12d9a1939ec`  
**PR base / main baseline:** `78884c0f2609edbfc94a24e42d84824bff9eed20`

## 1. Executive summary

A3 passenger-only implementation and exact-head automated verification have passed. The Android app builds, passes trusted-navigation tests and lint, installs and launches in the Android 15 emulator, and passes the packaged WebView smoke check. The dependency/supply-chain triage is resolved for the package inputs scanned: the categorized Gradle CycloneDX SBOMs and frontend lockfile produced zero OSV findings.

A4 is **PARTIAL / NOT VERIFIED-CLOSED**. Internal source/configuration review and Owner-reported physical-device checks are recorded, but independent Android/WebView security review remains missing. External-keyboard interaction testing has not been performed; TalkBack is deferred by Owner. A zoom-persistence limitation remains documented.

PR #25 is OPEN / DRAFT / UNMERGED. No merge, deployment, release, production activation, real passenger-data processing, booking, ticketing or payment is authorized.

## 2. Stage-gate progress

Percentages below are project-tracking estimates. The overall gate-progress estimate is the equal-weight average of the five governance stages; it is not a production-readiness score.

| Stage | Progress | Disposition | Evidence / remaining gate |
|---|---:|---|---|
| A1 — assessment/spec/freeze | 100% | **VERIFIED-CLOSED** | Owner-approved closure record on branch `docs/a1-owner-approved-closure`, commit `e1c2fa8630268a6832000c5fc88793bdbb7c7612`, PR #24 |
| A2 — read-only reconciliation | 100% | **COMPLETED** | Decisions D01–D07 reconciled; clean A3 branch created from main baseline; no wholesale import of PR #14 |
| A3 — implementation | 100% | **IMPLEMENTED + AUTOMATED-VERIFIED** | Passenger-only guest preview, reviewed Android integration, dependency remediation and exact-head CI pass; PR remains unmerged |
| A4 — verification | 75% | **PARTIAL / NOT VERIFIED-CLOSED** | CI, internal review and Owner-reported device checks pass within stated scope; independent security review and remaining accessibility evidence are outstanding |
| A5 — deployment | 0% | **NOT STARTED** | Separate Owner approval and production/legal/security gates required |

**Overall stage-gate progress estimate: 75%.**  
**Overall readiness: DEVELOPMENT PREVIEW ONLY — NOT PRODUCTION READY.**

## 3. A3 implementation scope

### 3.1 Product and public-interface boundary

Implemented on the clean A3 branch:

- Passenger-only, Amharic-first / English-capable public development preview.
- Guest access retained; public login/registration and credential collection removed.
- Public driver, cargo/heavy-load and fleet registration/workspaces removed from the active product UI; their requirements are preserved as future scope.
- Public administrative navigation and privileged UI removed pending server-side authorization.
- Unsupported route distance, fare and service-availability claims removed.
- MaaleNex identity normalized across web, PWA and Android.
- Legacy Android package identifier retained pending a separately reviewed migration.

The preview does not implement or authorize real accounts, authentication, passenger-data collection, booking, ticketing, payment, dispatch, driver/cargo/fleet operations, administration or live service publication.

### 3.2 Android shell and WebView boundary

- Android packaged WebView shell uses local bundled frontend assets.
- No INTERNET permission or JavaScript bridge/native plugin is exposed.
- WebView file/content access is disabled; mixed content is blocked; unused DOM storage is disabled.
- Top-level trusted document is restricted to the exact packaged SPA entry document.
- CSP validation rejects duplicate directives, wildcard sources, unsafe-inline and unsafe-eval.
- Vite relative asset paths support packaged WebView loading.
- Pinch zoom is enabled with built-in controls hidden.
- Android backup is disabled and cleartext traffic is disabled.
- Trusted-navigation unit tests cover malformed URLs, host lookalikes, userinfo, schemes, ports, path traversal, query/fragment and non-entry document paths.

These are source/configuration and automated-test findings; they are not an independent penetration test.

## 4. Exact-head CI and security evidence

All listed workflows below ran against the same verified code/workflow head `c192a2439305e60a6cea0be75251b12d9a1939ec`.

| Workflow | Run | Result |
|---|---|---|
| Android shell verification | [#43719864854](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854) | **PASS** |
| OSV PR-diff scan | [#43719864941](https://github.com/akefadaka-git/maalenex/actions/runs/43719864941) | **PASS — no issues found** |
| Brand assets and frontend verification | [#43719864840](https://github.com/akefadaka-git/maalenex/actions/runs/43719864840) | **PASS** |
| Cloudflare Pages build | [#43719864735](https://github.com/akefadaka-git/maalenex/actions/runs/43719864735) | **PASS — deployment not executed** |

### 4.1 Android workflow detail

Run #43719864854 passed:

- Frontend install, tests and production asset build.
- CSP contract validation.
- Android SDK, Gradle 9.9.1 and Java 17 setup.
- Gradle SHA-256 dependency verification using committed metadata.
- Runtime, compile, test and build-tool dependency report capture.
- CycloneDX SBOM generation and the SBOM regression-validation gate.
- Trusted-navigation unit tests.
- Debug APK assembly and Android lint.
- Android 15 emulator install, launch and packaged WebView smoke test.

The emulator evidence confirms that the packaged entry document completed, the React root rendered non-empty text, the process remained alive, and no main-frame error, renderer loss, fatal exception or CSP violation was recorded.

### 4.2 Dependency and supply-chain result

The first metadata-based OSV scan produced 93 finding records across 22 unique package/version combinations. Configuration-level comparison showed:

- Application runtime: zero vulnerable matches.
- Main app compile classpath: zero vulnerable matches.
- Unit-test and Android-test classpaths: zero vulnerable matches.
- Seven affected package versions were in the Android/Gradle build-tool classpath.
- A separate `lintClassPath` project configuration was not exposed; lint tool dependencies are represented within the AGP build-tool graph.
- Netty findings came from optional CI Develocity injection, not the app graph. Develocity injection was disabled, and the final build-tool SBOM contains no Netty components.
- Apache HttpClient 4.5.6 was a requested version; Gradle selected 4.5.14, which is above the fixed version.

The seven build-tool dependencies were remediated:

| Component | Before | Selected after remediation |
|---|---:|---:|
| Guava | 33.4.0-jre | 33.7.2-jre |
| Commons Lang | 3.16.0 | 3.18.0 |
| jose4j | 0.9.5 | 0.9.6 |
| Bouncy Castle bcpkix | 1.79 | 1.85 |
| Bouncy Castle bcprov | 1.79 | 1.85 |
| JDOM2 | 2.0.6 | 2.0.6.1 |
| Kotlin Gradle Plugin | 2.2.10 | 2.4.21 |

The final full OSV scan read these inputs:

| Input | Package instances |
|---|---:|
| Android runtime SBOM | 27 |
| Android test SBOM | 29 |
| Android compile SBOM | 19 |
| Gradle build-tool SBOM | 112 |
| Frontend npm lockfile | 160 |
| **Total across inputs** | **347** |

OSV output: **No issues found.** The total is the sum across SBOM/lockfile inputs and is not a deduplicated count.

The workflow now scans resolved CycloneDX SBOMs and the frontend lockfile. Gradle verification metadata is retained as a SHA-256 integrity control, not misused as a resolved dependency lockfile. The PR-diff scanner is scoped to the frontend lockfile; the Android workflow performs the full Android and frontend SBOM scan.

See [Dependency and Supply-Chain Review v1.2](../security/PRELIMINARY-DEPENDENCY-SUPPLY-CHAIN-REVIEW-v1.0.md).

### 4.3 Artifacts and exact APK identity

Artifacts from Android run #43719864854 (30-day retention):

- [Debug APK](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163739417)
- [Android lint report](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164391194)
- [Trusted-navigation unit tests](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164580548)
- [WebView emulator smoke evidence](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164391345)
- [OSV SARIF — zero results](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163992272)
- [Resolved SBOM inputs](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164665214)
- [Gradle verification metadata](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163599898)

APK details:

- File: `app-debug.apk`
- Size: 2,643,438 bytes
- SHA-256: `ca6e2bb1617d6585cf3cdabd457821bbe8b1f1f9933740f3203b07dedc1d1b54`

This is a debug APK, not a production/release-signed package.

## 5. A4 physical-device and accessibility evidence

Owner-reported device: Samsung Galaxy A16 (SM A16), Android 16.

| Check | Result |
|---|---|
| Installation and launch | **PASS** |
| Amharic and English UI display | **PASS** |
| Pinch-to-zoom | **PASS** |
| Zoom retained after ordinary reopen | **PASS** |
| Zoom after full process termination and relaunch | **PARTIAL — resets** |
| Android system font scaling | **PASS** |
| Screen rotation | **PASS** |
| Increased Android Display size / narrow-layout usability | **PASS — no reported overlap or clipping** |
| External keyboard navigation | **NOT TESTED** — Owner has no external keyboard |
| TalkBack | **DEFERRED** by Owner |

The physical checks are Owner-reported, not independent laboratory evidence. Zoom reset after complete process termination is recorded as a persistence limitation, not a failure of the zoom control.

Source-level accessibility corrections include improved footer and language-control contrast, a focusable skip-link target, and header/main/footer landmark separation. Full WCAG 2.2 AA acceptance is not claimed.

## 6. Independent security review and residual risk

An independent Android/WebView review handoff packet has been refreshed to exact target commit `c192a2439305e60a6cea0be75251b12d9a1939ec` and the APK SHA-256 above.

**Independent reviewer sign-off: MISSING.**

The reviewer must independently assess:

- WebView navigation and subresource boundaries, redirects, malformed URL handling and external intent behavior.
- Android manifest, permissions, exported components, backup, cleartext policy and debug/release differences.
- Actual APK CSP, XSS/URL handling, packaged asset integrity and dependency/supply-chain risks.
- Dynamic device/emulator and proxy/network behavior.
- Exact reviewed commit and APK SHA-256, findings, residual risk and signed verdict.

Toolchain caveat: KGP 2.4.21 is documented as fully supported through Gradle 9.7.0; the project uses Gradle 9.9.1 for security fixes. The exact build passed on the verified head, but Gradle 9.9.1 is outside KGP's documented fully supported range. This remains a compatibility residual risk.

## 7. Governance and deployment boundary

- PR #25 remains OPEN / DRAFT / UNMERGED.
- Base branch remains `main` at `78884c0f2609edbfc94a24e42d84824bff9eed20`.
- No main-branch modification, merge or deployment was performed by this work.
- No production activation, real operator onboarding, real passenger-data processing, booking, ticketing, payments, dispatch or commercial operation is authorized.
- A5 deployment remains NOT STARTED and requires separate Owner approval.

## 8. Immediate next step

Obtain an independent security reviewer to assess the exact commit and debug APK identified in section 4.3, complete the remaining applicable keyboard/focus accessibility evidence without requiring an external keyboard, and record a signed verdict. TalkBack remains deferred unless the Owner changes that decision.

A4 must remain PARTIAL until the independent review and applicable remaining acceptance evidence are completed. Do not merge or deploy as part of this next step.
