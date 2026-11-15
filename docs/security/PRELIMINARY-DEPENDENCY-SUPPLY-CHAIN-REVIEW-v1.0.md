# MaaleNex — Dependency and Supply-Chain Review v1.1

**Status:** ACTIVE REMEDIATION — INTERNAL REVIEW; NOT AN INDEPENDENT AUDIT  
**Current application / Android verification target:** ae0fd402d42626e82b24c37ec46af0c3158bc680  
**Repository:** akefadaka-git/maalenex  
**PR:** #25

This v1.1 update supersedes the initial dependency observations in v1.0 where newer evidence exists. It does not certify production readiness or independent security review.

## 1. Frontend dependency controls

**Status: PASS for current lockfile and npm audit evidence.**

- A committed npm lockfile v3 now exists at `frontend/package-lock.json`.
- Lockfile inventory: 160 packages; package resolution and integrity metadata are recorded.
- Resolved direct versions include React 18.3.1, React DOM 18.3.1, Vite 8.3.8, Vitest 5.1.0 and @vitejs/plugin-react 6.3.0.
- Frontend CI uses Node 22 and `npm ci`, rather than resolving an unlocked dependency graph at build time.
- The blocking npm audit on the upgraded graph reported zero vulnerabilities.
- Exact-head frontend verification passed on PR head `bea1d49e91b91b6b1051737402e59cb07ec86e2c`: [run #43713719757](https://github.com/akefadaka-git/maalenex/actions/runs/43713719757).
- OSV PR scan for the frontend at that head passed: [run #43713719995](https://github.com/akefadaka-git/maalenex/actions/runs/43713719995).

The prior six npm findings (2 critical, 1 high, 3 moderate) were eliminated by the dependency upgrade and re-resolution. This statement applies to the new committed npm graph scanned by the successful audit, not to every tool or runtime dependency in the repository.

## 2. Android build-tool dependency findings

**Status: FINDINGS IDENTIFIED; REMEDIATION IN PROGRESS.**

The first complete Gradle verification bootstrap on PR head `bea1d49e91b91b6b1051737402e59cb07ec86e2c` completed the Android assemble, lint and emulator job successfully. Its OSV scan of the generated Gradle verification metadata reported:

- 16 packages with affected dependency records.
- 62 advisory records: 3 critical, 24 high, 33 medium, 1 low, 1 unknown.
- Affected package families in the scan output include Guava, protobuf-java, commons-io, Netty codec/http/http2/common/handler modules, commons-compress, Apache HttpClient, jose4j, Bouncy Castle, JDOM2 and the Kotlin Gradle plugin.
- The scanner attributed these records to `gradle/verification-metadata.xml`; it did not establish that all listed packages are shipped in the APK or reachable at runtime.
- The OSV workflow failed closed because the scan contained findings. This is not a clean scan and must not be represented as one.

Evidence: [Android shell verification run #43713719930](https://github.com/akefadaka-git/maalenex/actions/runs/43713719930). The Android build/emulator job succeeded; the downstream OSV job failed on the detected findings. SARIF artifact: [OSV Scanner SARIF](https://github.com/akefadaka-git/maalenex/actions/runs/43713719930/artifacts/14161548877).

### 2.1 Remediation applied for re-verification

The following version changes are now on the A3 branch:

- Android Gradle Plugin: 8.7.3 → 9.3.1.
- Kotlin Android Gradle plugin: 2.0.21 → 2.4.21.
- Gradle CI runtime: 8.9 → 9.9.1.
- AndroidX WebKit: 1.12.1 → 1.15.0 (selected to retain minSdk 23 compatibility).

Official compatibility evidence:
- AGP 9.3 requires Gradle 9.5 or newer; AGP 9.4 requires Gradle 9.6 or newer. https://developer.android.com/build/releases/about-agp
- Kotlin Gradle plugin 2.4.21 is documented as fully supported with Gradle through 9.7.0 and AGP through 9.3.1. Gradle 9.9.1 is newer than that fully supported range; the exact project build must therefore prove compatibility rather than assuming it. https://kotlinlang.org/docs/gradle-configure-project.html
- Gradle 9.9.1 is the current patch release and addresses three Gradle security vulnerabilities. https://docs.gradle.org/current/release-notes.html

The new exact-head workflows are running against `ae0fd402d42626e82b24c37ec46af0c3158bc680`:
- Android shell verification: [run #43714326716](https://github.com/akefadaka-git/maalenex/actions/runs/43714326716) — IN PROGRESS at this record.
- OSV dependency scan: [run #43714326830](https://github.com/akefadaka-git/maalenex/actions/runs/43714326830) — IN PROGRESS at this record.
- Frontend verification: [run #43714326381](https://github.com/akefadaka-git/maalenex/actions/runs/43714326381) — PASS.
- Cloudflare Pages build: [run #43714326389](https://github.com/akefadaka-git/maalenex/actions/runs/43714326389) — PASS; deployment was not performed.

The Android workflow now also captures `debugRuntimeClasspath` separately so the shipped application's runtime dependency graph can be distinguished from Gradle/AGP build-tool dependencies. That report has not yet been inspected at this record.

## 3. Required triage and closure conditions

1. Confirm the AGP 9.3.1 / Kotlin 2.4.21 / Gradle 9.9.1 build, tests, lint, APK assembly and emulator smoke all pass on the same exact head.
2. Inspect the captured `debugRuntimeClasspath` report and map every OSV finding to runtime, test-only, lint-only or build-tool-only configurations.
3. Review each advisory's affected-version range and exploitability context; do not blanket-suppress or label findings false positives.
4. Upgrade or constrain vulnerable dependencies where they are in an active build or runtime path. For any accepted residual finding, record package, advisory, configuration, reachability rationale, compensating control, owner and review date.
5. Re-run OSV on the exact resolved graph and retain the SARIF/report artifacts.
6. Commit generated Gradle verification metadata only after successful generation and scan triage; then rerun CI against the resulting final commit.
7. Obtain independent security reviewer sign-off against the exact final commit and APK SHA-256.

## 4. Current disposition

- Frontend lockfile / deterministic npm installation: **PASS**.
- Frontend npm audit: **PASS — zero findings on upgraded lockfile**.
- Frontend OSV PR scan: **PASS** on the previously scanned head.
- Android assemble/lint/emulator: **PASS** on the initial full-graph scan head; re-verification pending after toolchain upgrade.
- Android full Gradle dependency scan: **FINDINGS — 16 packages / 62 advisory records; remediation and runtime/build-time triage pending**.
- Android runtime dependency graph separation: **PENDING**.
- Gradle dependency verification metadata committed to branch: **NOT YET**; generated metadata is currently artifact-backed pending scan triage.
- Independent security review: **MISSING**.
- A4: **PARTIAL / NOT VERIFIED-CLOSED**.
- A5: **NOT STARTED**.

No merge, deployment, release, production activation, real passenger-data processing, or main-branch modification is authorized by this review.
