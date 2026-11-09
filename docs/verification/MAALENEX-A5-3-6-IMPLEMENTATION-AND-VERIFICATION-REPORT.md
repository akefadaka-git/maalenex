# MaaleNex A5.3.6 — Implementation and Verification Report

**Status:** SYNTHETIC HARNESS VERIFIED; LIVE F-04 ACCEPTANCE NOT RUN  
**Branch:** `a5/a5-3-6-provider-neutral-deployment-spec`  
**Draft PR:** [#13 — A5.3.6 provider-neutral deployment specification and synthetic edge acceptance harness](https://github.com/akefadaka-git/maalenex-moto/pull/13)  
**Parent PR:** [#11 — A5.3.4 edge security hardening](https://github.com/akefadaka-git/maalenex-moto/pull/11)  
**Parent commit:** `38be5af657f26335209bf908e3765a6b2e27c67a)

## 1. Scope completed

A5.3.6 prepared:
- Provider-neutral deployment topology, component boundaries, trust model and environment-separation specification.
- TLS, HSTS, CSP, proxy, CORS, cookies, ingress, caching, secrets, logging, monitoring and recovery requirements.
- Future gated deployment sequence and mapping to all F04-01–F04-12 acceptance gates.
- Offline standard-library Python evidence validator: `backend/scripts/a5_3_6_edge_acceptance.py`.
- Reserved `.invalid` synthetic fixture: `backend/tests/fixtures/a5_3_6_edge_acceptance.synthetic.json`.
- Regression tests: `backend/tests/test_a5_3_6_edge_acceptance.py`.
- No-network, no-secret, branch-scoped workflow: `.github/workflows/a5-3-6-synthetic-edge-acceptance.yml`.

## 2. Implementation and exact verification

The harness and fixture were committed on the isolated branch. The fail-closed input validation was then hardened to reject malformed non-object gate entries without crashing.

**Exact tested implementation HEAD:** `22c26c7f855117327a7d81b8ea74d2c4879f7cd2`  
**GitHub Actions PR run:** [#42574203977](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42574203977) — **SUCCESS**  
**Job:** Offline synthetic F-04 evidence validation — **SUCCESS**

Successful steps:
1. Checkout source.
2. Set up Python 3.12.
3. Compile harness and regression tests.
4. Run synthetic acceptance regression tests.
5. Validate the checked-in synthetic fixture.

The tests cover positive synthetic fixture validation, permanent non-evaluation of operational acceptance, endpoint-contact rejection, production-data/secret rejection, reserved-hostname enforcement, runtime-boundary drift, duplicate HSTS, CSP observation duration, unsafe CSP directives, method allowlisting, RTO compliance, prevention of synthetic Owner/deployment approval, malformed gate objects and missing gates.

The workflow has no network probes, endpoint URL input, cloud SDK, provider credentials, SMTP credentials, service container, deployment permission or production secret. The fixture uses a reserved `.invalid` hostname and synthetic references only.

## 3. Harness semantics and limitations

The harness emits `SYNTHETIC_PASS_NOT_LIVE` only for F04-01 through F04-11 when the synthetic fixture assertions pass. It always emits F04-12 as `NOT_EVALUATED`. Its overall production acceptance result remains `NOT_EVALUATED_NO_LIVE_EDGE_EVIDENCE`.

This is intentionally not a production edge scanner or provider configuration validator. It cannot prove TLS, headers, redirects, CSP browser behavior, public origin isolation, real proxy trust, WAF/rate limits, cache behavior, alert delivery, legal readiness or rollback at a deployed edge.

## 4. Safety and governance verification

| Control | Result |
|---|---|
| `APP_ENV` development/test only | Preserved; harness rejects other values |
| `SYNTHETIC_DATA_ONLY=true` | Preserved; harness requires true |
| Database loopback-only `maalenex_dev` | Preserved; harness rejects remote host/name |
| Provider/account/purchase/provisioning | NOT PERFORMED |
| DNS/certificate/hosting/network/runtime changes | NOT PERFORMED |
| Production secrets or keys | NOT generated, retrieved, stored or changed |
| Live endpoint/browser/TLS tests | NOT RUN |
| Real personal data, email/SMS, payments, GPS | NOT USED |
| Merge/deployment/production activation | NOT PERFORMED |

PR #13 is draft/open/unmerged and targets the A5.3.4 feature branch. PR #11 remains separate and unmerged. The default branch is not targeted by this PR.

## 5. Disposition

- Provider-neutral deployment specification: **PREPARED**.
- Synthetic fixture validator and regression tests: **VERIFIED** on the exact tested HEAD above.
- No-network CI: **PASS**.
- F04-01 design: **DESIGN-RESOLVED** under A5.3.5; operational evidence remains pending.
- F04-02 through F04-11: **NOT RUN operationally**; synthetic assertions do not count as live acceptance.
- F04-12: **PENDING Owner decision**; synthetic harness cannot assert approval.
- F-04 overall: **DESIGN-RESOLVED / OPERATIONAL ACCEPTANCE PENDING**.
- Overall A5 production readiness: **NOT READY / NO-GO**.

A5.3.6 preparation does not authorize provider selection, infrastructure, DNS/certificates, production secrets, runtime guard changes, deployment, merge or production activation. Those remain separate explicit Owner gates.


## 6. Final report/specification HEAD verification

After the implementation report and specification cross-reference were committed, the branch's documentation-inclusive HEAD was `b6c06ada3d49dfa5313c603bba26c82408302368`.

- Push workflow [#42574266512](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42574266512): **SUCCESS**.
- Pull-request workflow [#42574272458](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42574272458): **SUCCESS**.
- Both runs checked out the exact `b6c06ada3d49dfa5313c603bba26c82408302368` head and passed compilation, synthetic regression tests and checked-in fixture validation.

The implementation code's focused run remains [#42574203977](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42574203977) on `22c26c7f855117327a7d81b8ea74d2c4879f7cd2`. No application runtime code was changed in this stage.
