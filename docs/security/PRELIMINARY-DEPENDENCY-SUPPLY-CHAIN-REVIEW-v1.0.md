# MaaleNex — Dependency and Supply-Chain Review v1.2

**Status:** RESOLVED FOR THE SCANNED GRAPHS — INTERNAL REVIEW; NOT AN INDEPENDENT AUDIT  
**Repository:** `akefadaka-git/maalenex`  
**PR:** [#25](https://github.com/akefadaka-git/maalenex/pull/25)  
**Verified code/workflow head:** `c192a2439305e60a6cea0be75251b12d9a1939ec`  
**Base:** `main` at `78884c0f2609edbfc94a24e42d84824bff9eed20`  
**Verification date:** 2026-11-15

This v1.2 record supersedes the open dependency-triage disposition in v1.1. It records the exact resolved Gradle graphs, remediation versions, CI scans and artifacts. It does not certify production readiness, replace an independent security review, or prove the absence of unknown vulnerabilities.

## 1. Executive disposition

**PASS — zero known OSV findings in the resolved dependency inputs scanned on the verified head.**

The final exact-head Android workflow [#43719864854](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854) completed successfully. Its downstream OSV scan [job 132830678963](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854) reported **“No issues found.”**

The scan covered four CycloneDX 1.5 Gradle SBOMs generated from resolved Gradle dependency reports and the committed frontend npm lockfile. The Android workflow also verified the committed Gradle SHA-256 dependency metadata, ran the SBOM validation gate, trusted-navigation tests, APK assembly, lint and Android 15 emulator smoke.

This is a point-in-time scan of the enumerated package inputs, not a claim that the whole system is invulnerable. Independent Android/WebView security review remains **MISSING**.

## 2. Initial findings and configuration-level triage

The earlier metadata-based OSV scan produced 93 finding records, 52 advisory rules and 22 unique package/version combinations (3 critical, 21 high, 26 medium, 2 low). That scan treated Gradle verification metadata as a package inventory. Verification metadata is a checksum/integrity file and does not preserve the resolved configuration or distinguish selected versions from requested versions.

The generated Gradle reports were therefore compared with the SARIF package/version records:

| Configuration | Vulnerable matches in the captured resolved graph |
|---|---:|
| `debugRuntimeClasspath` — application runtime | **0** |
| `debugCompileClasspath` — application compile | **0** |
| Unit-test and Android-test classpaths | **0** |
| Separately exposed `lintClassPath` | Not available as a project configuration |
| Root Gradle/AGP build-tool classpath | **7 affected package versions** |

Lint dependencies are represented by the Android Gradle Plugin build-tool classpath in this project; no separate `lintClassPath` configuration was exposed. This limitation is recorded rather than inventing a lint-only classification.

### 2.1 Confirmed build-tool dependency remediations

| Component | Previously selected | Selected after remediation |
|---|---:|---:|
| `com.google.guava:guava` | 33.4.0-jre | **33.7.2-jre** |
| `org.apache.commons:commons-lang3` | 3.16.0 | **3.18.0** |
| `org.bitbucket.b_c:jose4j` | 0.9.5 | **0.9.6** |
| `org.bouncycastle:bcpkix-jdk18on` | 1.79 | **1.85** |
| `org.bouncycastle:bcprov-jdk18on` | 1.79 | **1.85** |
| `org.jdom:jdom2` | 2.0.6 | **2.0.6.1** |
| `org.jetbrains.kotlin:kotlin-gradle-plugin` | 2.2.10 | **2.4.21** |

The pins are declared on the Android root buildscript classpath in `android/build.gradle.kts`. The buildscript repositories are explicit (Google Maven, Maven Central and Gradle Plugin Portal). The Android workflow's SBOM validation gate asserts these selected versions and rejects regression to the previously affected versions.

The Kotlin Gradle Plugin finding corresponded to CVE-2026-53914 / GHSA-r937-wjx7-w2jp. The advisory fixes the issue in KGP 2.4.20-Beta1 and later; this project selects stable KGP 2.4.21. https://osv.dev/vulnerability/GHSA-r937-wjx7-w2jp

### 2.2 Findings that were not shipped application dependencies

- **Netty:** the affected Netty records appeared in the initial verification-metadata scan but not in the project's root build environment, app compile/runtime/test/lint reports or the final build-tool SBOM. The CI logs showed the optional Develocity init-script injection. The Android workflow now disables optional Develocity injection, and the final build-tool SBOM contains zero `io.netty` components. These were external CI build-instrumentation dependencies, not APK dependencies.
- **Apache HttpClient:** the old graph contained a request for 4.5.6, but Gradle selected **4.5.14**. The final build-tool SBOM records 4.5.14, above the advisory's fixed version 4.5.13. This was a requested-versus-selected-version metadata false positive, not a vulnerable selected artifact.
- No vulnerability suppression, advisory ignore, or blanket exception was added.

## 3. Corrected scan inputs and reproducible controls

The workflow now keeps two distinct input classes:

1. **Integrity metadata:** `android/gradle/verification-metadata.xml`, generated with SHA-256 verification and committed to the A3 branch. It is retained as an integrity control and is not passed to OSV as a dependency lockfile.
2. **Resolved dependency inventories:** CycloneDX 1.5 SBOMs generated from actual Gradle dependency reports, plus `frontend/package-lock.json`. OSV scans these resolved inputs.

The committed generator is `.github/scripts/gradle-report-to-cyclonedx.py`. The CI gate `.github/scripts/verify-gradle-sbom.py` validates the four SBOMs, their unique package URLs, all seven remediation pins, selected HttpClient 4.5.14, absence of the known vulnerable versions and absence of Netty components after disabling optional Develocity injection.

The PR-diff OSV workflow scans `./frontend` with `--allow-no-lockfiles`. The base branch does not yet contain the frontend lockfile, so this allows the base comparison to complete without pretending the base has dependencies. The Android workflow performs the full frontend-plus-Android SBOM scan.

## 4. Final exact-head scan evidence

**Verified head:** `c192a2439305e60a6cea0be75251b12d9a1939ec`

- Android shell verification [run #43719864854](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854) — **PASS**.
- Android full SBOM OSV scan (job `132830678963`) — **PASS; No issues found**.
- OSV PR-diff scan [run #43719864941](https://github.com/akefadaka-git/maalenex/actions/runs/43719864941) — **PASS; No issues found**.
- Brand assets and frontend verification [run #43719864840](https://github.com/akefadaka-git/maalenex/actions/runs/43719864840) — **PASS**.
- Cloudflare Pages build [run #43719864735](https://github.com/akefadaka-git/maalenex/actions/runs/43719864735) — **PASS**; deployment steps were not executed.

### 4.1 Exact package inventory scanned

| Input | Packages |
|---|---:|
| Android runtime SBOM | 27 |
| Android test SBOM | 29 |
| Android compile SBOM | 19 |
| Gradle build-tool SBOM | 112 |
| Frontend npm lockfile | 160 |
| **Total package instances across inputs** | **347** |

The total is the sum of the five inputs; it is not a deduplicated package count. OSV reported zero known issues across these inputs.

### 4.2 Build and artifact evidence

Artifacts from Android run #43719864854 (retention 30 days):

- [Resolved SBOM inputs](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164665214)
- [Gradle verification metadata](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163599898)
- [OSV SARIF — zero results](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163992272)
- [Debug APK](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14163739417)
- [Android lint report](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164391194)
- [Trusted-navigation unit-test report](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164580548)
- [WebView emulator smoke evidence](https://github.com/akefadaka-git/maalenex/actions/runs/43719864854/artifacts/14164391345)

Debug APK SHA-256:

`ca6e2bb1617d6585cf3cdabd457821bbe8b1f1f9933740f3203b07dedc1d1b54`

APK size: 2,643,438 bytes. This is the debug APK artifact, not a production/release-signed package.

## 5. Toolchain compatibility and residual risks

- AGP is 9.3.1; Gradle CI runtime is 9.9.1; KGP is 2.4.21.
- The exact combination passed assemble, unit tests, lint, APK creation and Android 15 emulator smoke on the verified head.
- Kotlin's published compatibility table documents KGP 2.4.21 as fully supported through Gradle 9.7.0 and AGP 9.3.1. Gradle 9.9.1 is outside that documented fully supported Gradle range. It is retained because Gradle 9.9.1 includes security fixes; the exact CI pass is positive compatibility evidence, but does not remove the vendor support-matrix caveat.
- Android Gradle Plugin built-in Kotlin migration / upgrade guidance: https://developer.android.com/build/migrate-to-built-in-kotlin
- Kotlin Gradle compatibility guidance: https://kotlinlang.org/docs/gradle-configure-project.html
- Gradle 9.9.1 release notes: https://docs.gradle.org/current/release-notes.html
- OSV SBOM scanning documentation: https://google.github.io/osv-scanner/usage/scan-source/

Zero OSV findings means no known advisories matched the scanned package inputs at scan time. It is not a penetration test, proof of reachability, code audit, runtime exploitability assessment, or guarantee against future advisories.

## 6. Final disposition

| Control | Status |
|---|---|
| Frontend lockfile and npm audit | **PASS** |
| Gradle SHA-256 dependency verification metadata | **PASS — committed** |
| Resolved runtime/compile/test/build-tool graph capture | **PASS** |
| Categorized CycloneDX SBOM generation and validation | **PASS** |
| Android and frontend OSV scan | **PASS — zero findings** |
| Android assemble, unit tests, lint and emulator smoke | **PASS** |
| Independent Android/WebView security review | **MISSING** |
| Full production security certification | **NOT PERFORMED** |
| A4 | **PARTIAL / NOT VERIFIED-CLOSED** |
| A5 deployment | **NOT STARTED** |

The independent review handoff packet must be updated to this exact head and APK hash, then reviewed and signed by an independent reviewer. No merge, deployment, release, production activation, real passenger-data processing, booking, ticketing or payment is authorized by this record.
