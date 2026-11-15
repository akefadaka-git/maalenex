# MaaleNex — Preliminary Dependency and Supply-Chain Review v1.0

**Status:** PRELIMINARY INTERNAL REVIEW — NOT AN INDEPENDENT AUDIT  
**Application review target:** e2dd491757a919b87a5f26478982f758493ecb6f  
**Repository:** ake fadaka-git/maalenex  
**PR:** #25

## Scope and method

This note records a source-level inspection of dependency declarations and the frontend verification workflow at the exact application review target. It does not claim a complete dependency inventory, vulnerability scan, malware scan, reproducible build, or independent security assessment.

Files inspected:
- frontend/package.json (blob 42c5f617772d94f6175102120f4ba64594d35149)
- android/build.gradle.kts (blob c7ad7549e74f63b6958ba4e171cc08161976da49)
- android/app/build.gradle.kts (blob 9fcc2e5580376da7efcb351d4994e8219801758a)
- android/settings.gradle.kts (blob 587c586781388b6f5a92ec6971426870fbdd8367)
- android/gradle.properties (blob 6c5ec4ed4945ec59113f3815a200b99475f83e8a)
- .github/workflows/a3-verify.yml (blob 536adff08af01a9923e95af4ca12755fe581e02b)

## Preliminary findings

### SUPPLY-001 — No committed npm lockfile found at reviewed target

**Severity:** Medium (supply-chain/reproducibility control gap; not evidence of a known exploitable vulnerability)  
**Evidence:** frontend/package.json declares semver ranges, including React ^18.3.1, Vite ^5.4.11 and Vitest ^2.1.5. A frontend/package-lock.json was not present at the reviewed target. The workflow runs npm install --no-audit --no-fund, which resolves dependencies without a committed lockfile and explicitly suppresses npm's audit step.  
**Impact:** Dependency resolution can vary between builds; exact transitive versions are not established by the repository snapshot. A reviewer cannot reliably reproduce the dependency graph from this commit alone. The current CI pass establishes that the build/test ran, not that dependencies were vulnerability-free.  
**Required action:** Generate and commit a reviewed package-lock.json; change CI to npm ci; add a separate dependency-audit step that records results and does not silently ignore high/critical findings. Pin or otherwise control Node/npm toolchain versions. Re-run exact-head CI and review resulting lockfile diffs.

### SUPPLY-002 — Android dependency freshness and transitive resolution are not yet evidenced

**Severity:** Low / Informational pending full resolution  
**Evidence:** Android Gradle plugin 8.7.3, Kotlin Android plugin 2.0.21, AndroidX WebKit 1.12.1, AndroidX Core KTX 1.15.0 and JUnit 4.13.2 are declared. No Gradle dependency lockfiles or dependency verification metadata were found at the inspected conventional paths.  
**Impact:** Direct versions are visible, but the complete resolved transitive graph, integrity verification and current advisory status have not been established. AndroidX WebKit 1.12.1 is substantially older than the AndroidX release page's stable 1.18.0 entry dated 2026-10-21 / latest update 2026-11-04. This is a freshness review item, not a claim that 1.12.1 contains a confirmed vulnerability.  
**Required action:** Resolve and record the complete Gradle graph; run dependency vulnerability scanning; assess an upgrade to a current stable WebKit release in a separate tested change; enable Gradle dependency locking and dependency verification where practical.

### SUPPLY-003 — No repository evidence yet of automated dependency advisory monitoring

**Severity:** Low / Informational pending broader repository inspection  
**Evidence:** The inspected frontend workflow does not run npm audit or an equivalent dependency scanner. The Android workflow evidence reviewed to date establishes build/lint/test execution, not dependency advisory scanning.  
**Impact:** Vulnerability detection is not demonstrated by the current CI evidence.  
**Required action:** Add automated advisory scanning for npm and Gradle dependencies, with documented triage, suppression justification, and update cadence. Confirm whether repository-level Dependabot or equivalent controls already exist before duplicating them.

## Advisory research notes

- The official Vite advisory index contains multiple 2026 advisories, including issues specifically scoped to newer Vite major versions and development-server behavior. Their existence does not by itself establish that this project's declared Vite 5.4.11 or production bundle is affected. Exact package versions and affected-version ranges must be checked against a lockfile and usage context.
- The Vitest advisory index also lists 2026 issues, some scoped to Browser Mode or newer Vitest versions. No applicability conclusion is made for the declared Vitest 2.1.5 without an exact resolved graph and advisory range analysis.
- Android Developers' AndroidX WebKit release notes show stable 1.18.0 as the current release entry in late October/early November 2026; the project's declared 1.12.1 should be reviewed for upgrade, compatibility and regression risk.

References:
- Vite advisories: https://github.com/vitejs/vite/security/advisories
- Vitest advisories: https://github.com/vitest-dev/vitest/security/advisories
- AndroidX WebKit release notes: https://developer.android.com/jetpack/androidx/releases/webkit

## Required next verification

1. Create and review the npm lockfile.
2. Run npm audit against the locked graph and document all findings.
3. Resolve Gradle dependencies and produce a full dependency inventory.
4. Run an Android/Gradle vulnerability scan against the exact resolved graph.
5. Review any proposed updates and rerun frontend, Android lint, unit tests, APK assembly and emulator smoke.
6. Have the independent reviewer verify the resulting exact commit and APK SHA-256.

## Disposition

- Preliminary source-level dependency review: PARTIAL.
- Known exploitable vulnerability confirmed in this note: NONE ESTABLISHED.
- Dependency vulnerability scan: NOT RUN / NOT EVIDENCED.
- Reproducible npm dependency graph: MISSING.
- Independent security review: MISSING.
- A4: remains PARTIAL / NOT VERIFIED-CLOSED.
- No merge, deployment, release, production activation or main-branch modification is authorized.
