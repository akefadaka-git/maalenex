# MaaleNex Moto — A5 Production Deployment-Readiness Assessment

**Document status:** Assessment baseline — NOT a deployment authorization  
**Stage:** A5 readiness assessment only; deployment, merge, production activation and public launch are excluded  
**Repository:** `akefadaka-git/maalenex-moto`  
**Assessment branch:** `a5/deployment-readiness-assessment`  
**Assessment base:** A4 verified HEAD `d54b0291a58499891baaac5d5106ea8eed85a96b`  
**Assessment date:** 2026-11-09  
**Product scope considered:** MaaleNex Moto passenger mobility platform, Ethiopia-first; initial pilot intent Koybe / Maale Woreda / South Omo, with Jinka operations and regional route discovery contemplated  
**Decision:** **NOT READY FOR PRODUCTION — READINESS EVIDENCE IS INSUFFICIENT AND THE CURRENT APPLICATION CONFIGURATION EXPLICITLY BLOCKS NON-DEVELOPMENT RUNTIMES.**

---

## 1. Executive assessment

This document assesses the evidence required before any production deployment or live operation. It does not deploy, provision infrastructure, create production credentials, change application runtime guards, enable customer data processing, activate payments, enable GPS tracking, onboard real operators, or authorize commercial transport operations.

The A4 CI baseline is useful software verification evidence, but it is not production assurance. The repository's current configuration enforces both:
- `APP_ENV` must be `development` or `test`; and
- `SYNTHETIC_DATA_ONLY` must remain true.

It also restricts the configured PostgreSQL host to loopback and the database name to `maalenex_dev`. Therefore, a production environment cannot be configured by merely supplying a production URL; the current code intentionally rejects it. This is a deliberate safety boundary, not a defect to bypass. Any future production-mode architecture must be separately specified, reviewed, tested, and explicitly authorized.

The repository's current `SECURITY.md` says production deployment and processing are not authorized. The README likewise states that live operator onboarding, real passenger bookings, production personal-data processing, payment collection, ticket issuance, boarding, production deployment and public service launch are not authorized.

### Overall disposition

| Domain | Assessment |
|---|---|
| Production infrastructure and hosting | **NOT EVIDENCED** |
| Production runtime / configuration | **BLOCKED BY CURRENT SAFETY GUARDS** |
| Secrets and cryptographic key lifecycle | **NOT READY / NOT EVIDENCED** |
| TLS, ingress and network security | **NOT EVIDENCED** |
| Backup, restore and disaster recovery | **NOT EVIDENCED** |
| Monitoring, alerting and incident response | **NOT EVIDENCED** |
| Privacy and personal-data governance | **NOT READY / NOT EVIDENCED** |
| Operational support and service governance | **NOT EVIDENCED** |
| Transport, corporate, tax and payment regulatory readiness | **NOT READY / LEGAL DETERMINATIONS REQUIRED** |
| Deployment and live operation | **NOT AUTHORIZED** |

No readiness percentage is assigned: most controls have no production evidence, and a numerical percentage would imply a level of validation that has not occurred.

---

## 2. Assessment method and evidence standard

Use the following labels consistently:

- **PASS:** current, inspectable evidence proves the control is implemented and effective in the intended production environment.
- **PARTIAL:** some implementation or evidence exists, but important requirements remain.
- **BLOCKED:** a known condition prevents safe progression.
- **NOT EVIDENCED:** no reliable production evidence was available during this assessment.
- **NOT APPLICABLE:** documented rationale proves the control does not apply to the approved launch scope.
- **NOT RUN:** a required test or exercise has not been performed.

A repository setting, passing unit test, CI scan, local development run, or synthetic-only email test is not evidence that a production control is operational. Each PASS requires a dated artifact, accountable owner, scope, and verifiable test or configuration evidence.

This assessment is based on the A4 repository evidence inspected at the assessment base, including:
- `backend/app/core/config.py`
- `.env.example`
- `README.md`
- `SECURITY.md`
- A4 exact-head automated verification evidence recorded in the repository and GitHub Actions.

It does not have access to or evidence of a production cloud account, hosting subscription, DNS zone, production database, production secrets store, insurance contracts, licenses, tax registration, or regulator correspondence. Those are therefore not presumed to exist.

---

## 3. Production infrastructure and architecture

**Current status: NOT EVIDENCED; runtime BLOCKED for production.**

### Required target architecture

Before selecting a hosting provider, document and approve:
1. Hosting provider, account owner, legal contracting entity, region and data residency location.
2. Production topology and trust boundaries: public ingress, TLS termination, frontend hosting, API runtime, PostgreSQL, background jobs, object/file storage, email provider, observability and administrative access.
3. Network segmentation; private database access; outbound egress allowlists; no public database listener.
4. Separate development, staging and production accounts/projects, networks, databases, credentials and encryption keys.
5. Infrastructure-as-code or an equivalent reproducible configuration, with change review and rollback.
6. Capacity, availability, low-bandwidth/mobile performance, regional connectivity, power/network interruption and provider-failure assumptions for Koybe / Jinka.
7. Data residency and cross-border processing assessment before choosing a region or SaaS service.
8. Cost ceiling, billing owner, renewal responsibility, provider support, service limits and exit/export plan. No paid resource is to be created as part of this assessment.

### Current repository findings

- `backend/app/core/config.py` rejects every `APP_ENV` except `development` and `test`.
- It rejects `SYNTHETIC_DATA_ONLY=false`.
- It rejects remote PostgreSQL hosts and any database name other than `maalenex_dev`.
- `.env.example` contains local development values.
- No production Dockerfile, deployment manifest, production infrastructure definition, provider topology, or production runbook was evidenced in the inspected paths.

**Required remediation before a production architecture can be considered:** create a separately approved production architecture and configuration specification. Do not remove these guards or weaken synthetic-only protections as an ad hoc deployment fix.

### Exit evidence

- Approved architecture and data-flow diagrams.
- Provider/account ownership and region decision.
- Infrastructure configuration review and reproducible staging deployment evidence.
- Private database connectivity and network isolation test.
- Capacity/load and failure-mode test results.
- Documented rollback and provider exit procedure.

---

## 4. Secrets and cryptographic key lifecycle

**Current status: NOT READY / NOT EVIDENCED.**

The application has configuration fields for identity encryption and lookup keys, SMTP credentials, and email delivery. Existing GitHub Actions SMTP credentials and ephemeral test keys are test/CI evidence only; they are not production key-management evidence.

### Required controls

1. Use a managed secrets manager or equivalent protected secret store; do not place production secrets in Git, repository files, client bundles, container images, logs, chat, tickets or ordinary CI variables.
2. Separate production secrets from CI, staging and developer credentials.
3. Use unique, high-entropy production values for identity encryption and lookup/HMAC keys, database credentials, SMTP/API credentials, session-signing material and any future provider integration.
4. Define key ownership, generation ceremony, access approval, least privilege, storage, backup/recovery, rotation cadence, revocation, compromise response and destruction.
5. Document encryption-key versioning and re-encryption/migration strategy before rotating keys that protect stored identity data.
6. Ensure lookup-key rotation has a safe dual-read / controlled re-index migration plan so account lookup does not silently fail.
7. Rotate credentials after suspected exposure, personnel departure, provider change or compromise; audit every privileged secret access.
8. Require MFA and tightly scoped access for cloud, source-control, DNS, database and secrets administration.
9. Keep production secrets unavailable to untrusted pull-request workflows and ordinary build/test jobs.
10. Redact credentials, bearer tokens, challenge tokens, personal data and sensitive request payloads from logs and error reporting.

### Exit evidence

- Approved secrets inventory with purpose, owner, environment and rotation schedule (never values).
- Secrets-manager configuration and IAM/access review.
- Key-generation and rotation runbook.
- Successful staging rotation and revocation exercises.
- Evidence of log redaction and secret-scanning coverage.
- Documented backup/recovery of key material with controlled access.

**Do not paste secrets into this repository or conversation.**

---

## 5. TLS, ingress and network security

**Current status: NOT EVIDENCED.**

The application includes a `secure_cookies` setting and a helper that considers HTTPS request scheme, and prior passenger-foundation testing addressed Secure cookies behind a TLS-terminating proxy. That is not evidence of an operational production TLS endpoint or trusted proxy configuration.

### Required controls

- Domain ownership and DNS control documented; registrar and DNS MFA enabled.
- TLS certificates issued by a trusted CA, automatic renewal monitored, expiry alerts tested.
- HTTPS-only ingress; HTTP redirects to HTTPS; HSTS only after correct HTTPS coverage is confirmed.
- Modern TLS configuration; disable obsolete protocols and weak cipher suites.
- Secure, HttpOnly, appropriately scoped SameSite cookies; CSRF protection; no session cookies over HTTP.
- Trusted proxy/header configuration explicitly allowlisted; never trust arbitrary client-supplied forwarded headers.
- Strict CORS allowlist for production origins; no localhost origins in production.
- API ingress rate limits, request-size limits, timeouts, abuse protection and DDoS/provider controls.
- Database, cache and administrative services not exposed to the public internet.
- Security headers and content-security policy appropriate to the application.
- Certificate renewal, DNS failover and ingress outage runbooks.

### Exit evidence

- External TLS scan and configuration report for every production hostname.
- Browser/API verification of cookie flags, CORS, redirects and security headers.
- Trusted-proxy integration tests.
- DNS and certificate renewal test evidence.

---

## 6. Backups, recovery and business continuity

**Current status: NOT EVIDENCED; recovery capability unproven.**

### Required controls

1. Define business-approved Recovery Time Objective (RTO) and Recovery Point Objective (RPO) for identity, bookings/reservations, audit records and service registry.
2. Establish automated encrypted PostgreSQL backups and point-in-time recovery where supported.
3. Keep backups logically and administratively separate from the production database account; protect against deletion, ransomware and compromised credentials.
4. Define retention and secure deletion in line with legal and privacy requirements.
5. Back up required object/document data and configuration, not just the relational database.
6. Define encryption-key recovery dependencies; a database backup is unusable if required decryption keys are lost.
7. Create restore runbooks with named operators, approval requirements and integrity checks.
8. Test a full restore into an isolated environment, including schema migration compatibility, identity decryption, audit continuity and booking consistency.
9. Define disaster scenarios: hosting-region failure, database corruption, accidental deletion, credential compromise, connectivity outage, provider termination and key loss.
10. Establish business continuity procedures for a low-connectivity pilot, including manual fallback and reconciliation controls, without silently duplicating bookings or payments.

### Exit evidence

- Approved RTO/RPO.
- Backup schedule, retention and encryption configuration.
- At least one successful timed restore exercise with measured RPO/RTO.
- Integrity/reconciliation report and named recovery owners.
- Key-recovery exercise.
- Disaster recovery and continuity runbook.

---

## 7. Monitoring, logging and incident response

**Current status: NOT EVIDENCED.**

### Required controls

- Centralized structured application, infrastructure, database and security logs.
- Correlation/request IDs and synchronized time sources.
- No passwords, tokens, full identity values, payment credentials or unnecessary personal data in logs.
- Audit trails for privileged access, identity lifecycle, account recovery, administrative actions, data access/export and security configuration changes.
- Metrics and alerting for uptime, latency, error rate, database saturation/connections, queue backlog, failed email delivery, authentication abuse, rate-limit triggers, backup failures, certificate expiry and resource exhaustion.
- Health checks that distinguish process liveness from database and dependency readiness.
- On-call ownership, escalation path, severity definitions and incident communications.
- Security incident response plan with containment, evidence preservation, credential/key revocation, recovery and post-incident review.
- Privacy breach triage and regulator/data-subject notification procedures aligned with applicable Ethiopian law.
- Log retention, access controls, tamper resistance and deletion schedule.

### Required exercises

- Simulate API outage, database unavailable, failed backup, compromised credential, unusual authentication volume and privacy incident.
- Verify alerts reach a monitored destination and are acknowledged.
- Verify that incident logs do not disclose secrets or sensitive personal data.

### Exit evidence

- Monitoring dashboard and alert inventory.
- Tested alert delivery and escalation.
- Incident response plan and exercise report.
- Audit/log access review and retention policy.

---

## 8. Privacy and personal-data governance

**Current status: NOT READY / NOT EVIDENCED.**

The platform's future live operation may process passenger, driver, operator, staff, contact, booking, trip and potentially location data. No live personal-data processing is authorized by this assessment.

Ethiopia's **Personal Data Protection Proclamation No. 1321/2024** is an applicable primary legal reference. Its published framework includes lawful and transparent processing, purpose limitation, data minimization, accuracy, storage limitation, integrity/confidentiality/security, data sovereignty, controller/processor obligations, technical and organizational measures, DPIA, DPO designation, processing records, breach notification and data protection by design/default. Exact obligations, exemptions, implementation directives and applicability to MaaleNex's controller/processor roles must be confirmed by Ethiopian counsel and the competent authority before launch.

### Required controls

1. Map data flows and decide controller, joint-controller and processor roles for MaaleNex, transport operators, communications vendors, cloud hosts, payment providers and other partners.
2. Create a Record of Processing Activities (RoPA): purpose, lawful basis, data categories, data subjects, recipients, processors, cross-border transfers, retention and deletion.
3. Conduct and approve a Data Protection Impact Assessment (DPIA) before high-risk processing, including location tracking, identity verification and profiling if introduced.
4. Determine and document lawful basis for each processing purpose; consent must not be treated as a universal substitute for other lawful bases.
5. Publish clear Amharic-first and accessible privacy notices with appropriate English support.
6. Implement data-subject request processes: access, correction, deletion, objection/withdrawal where applicable, and response tracking.
7. Define age/minor handling and avoid collecting children's data unless legal basis and safeguards are established.
8. Minimize identity-document collection; do not collect or retain full identity documents unless strictly necessary and legally justified.
9. Define precise location-data purpose, permission, granularity, retention, access and user-visible controls. No silent or continuous GPS tracking.
10. Establish processor agreements, subprocessor inventory, security obligations, breach cooperation and deletion/return clauses.
11. Assess cross-border transfer and data sovereignty requirements before using foreign cloud, analytics, email, maps or support vendors.
12. Define retention schedules by data class, legal hold and verifiable deletion from primary systems and backups.
13. Appoint/designate a Data Protection Officer where required and establish accountable privacy governance.
14. Create a breach-response workflow that can meet the applicable statutory notification deadline; the Proclamation's breach-notification provision is commonly summarized as a 72-hour notice to the Authority after awareness. Counsel must confirm the operative text, trigger, scope and any current implementing rules.
15. Complete a privacy-by-design review of analytics, crash reporting, support tooling, exports and audit logs.

### Exit evidence

- Written legal applicability assessment.
- Approved RoPA and DPIA.
- Approved privacy notices and consent/permission UX.
- DPO designation or reasoned legal determination.
- Data-subject request and deletion tests.
- Processor contracts and cross-border transfer assessment.
- Tested privacy incident/breach playbook.

---

## 9. Operational controls and service governance

**Current status: NOT EVIDENCED.**

### Required controls

- Legal entity incorporation completed and legal contracting authority confirmed; MaaleNex Technologies PLC is currently described as in formation.
- Clear service operator/intermediary/agent role and responsibility matrix.
- Named accountable owners for product, engineering, security, privacy, transport operations, customer support, finance and incident command.
- Staff/admin MFA, role-based access, joiner/mover/leaver controls, quarterly access reviews and privileged session logging.
- Documented change management, peer review, protected branches, CI gates, release approvals, rollback and emergency change process.
- Support channels and service hours in Amharic and English, complaint escalation, lost-property/safety incident handling and refund/cancellation policies where relevant.
- Operator onboarding verification, driver and vehicle document checks, periodic revalidation and suspension workflow.
- Passenger safety escalation, emergency contact procedure, incident reporting and cooperation with competent authorities.
- Transparent fares, fees, booking terms, cancellation/refund rules, service availability and operator identity.
- Supplier and subprocessor due diligence, contract register, service-level commitments and exit plans.
- Staff training on privacy, security, customer safety, fraud, incident response and records handling.
- Operational runbooks for service disruption, reconciliation, customer communications and data correction.
- Separate go/no-go decision for each service line; initial passenger scope must not silently activate Transit, Delivery, Cargo, Market, Fleet, Business or Pay.

### Exit evidence

- Signed responsibility matrix and operating model.
- Support, safety, complaints and incident SOPs.
- Access review and staff training records.
- Operator/driver/vehicle verification policy and sample audit.
- Service-specific launch checklist and customer terms.

---

## 10. Ethiopian regulatory and legal readiness

**Current status: NOT READY — legal classification, licenses, permits and documentary evidence are missing.**

This section is a regulatory issue register, not a legal opinion. The exact obligations depend on whether MaaleNex is legally an operator, intermediary, booking agent, marketplace, technology provider or payment service participant, and on the specific vehicle, route, operator and service model. Obtain written advice from qualified Ethiopian counsel and written determinations from the competent federal/regional authorities. Do not infer that a software platform is exempt from transport rules.

### 10.1 Corporate, trade and tax

Before contracting or operating:
- Complete PLC incorporation and obtain current commercial registration, business license and tax registrations for the correct business activities.
- Confirm the correct business-activity classification for technology platform, booking/intermediation and any transport-related activity.
- Confirm VAT, withholding, income-tax, invoicing/e-invoicing and record-retention duties with the relevant tax authority.
- Confirm employment, contractor, social-security and workplace obligations for the actual staffing model.
- Verify regional/local permits and business premises requirements for Koybe, Jinka and any operating locations.

**Evidence:** incorporation certificate, commercial registration, business license, TIN/VAT status as applicable, tax/legal opinion, regional/local permits and compliance calendar.

### 10.2 Road transport and operator licensing

Primary reference: **Road Transport Proclamation No. 1274/2022**, listed by the Ministry of Justice as in force. A current amendment is **Commercial Road Public Transport Operators’ Organizational, Competency Assurance Licensing and Trip Implementation (Amendment) Directive No. 1136/2026**, dated 13 May 2026.

Before any passenger service:
- Obtain a written legal determination of MaaleNex's own licensing status and whether it is acting as a transport operator, broker, booking agent, marketplace or technology supplier.
- Identify the competent federal and regional transport authorities for the planned route and operating geography.
- Verify each transport operator's organization, competency certification, commercial license, route/operating authorization and trip implementation obligations.
- Verify each vehicle's registration, inspection/roadworthiness, permitted use, capacity and required documents.
- Verify each driver has the correct current qualification/license and is authorized for the vehicle/service.
- Verify route, terminal, schedule, fare/tariff and trip authorization requirements.
- Confirm rules for inter-regional routes, including Jinka–Wolaita Sodo and Addis Ababa, before advertising or accepting reservations.
- Do not represent a reservation reference or QR payload as a travel ticket or boarding authorization unless the regulatory and operator process explicitly supports it.

**Evidence:** written classification, regulator correspondence, operator/vehicle/driver verification records, route/terminal permits, approved trip/fare records and compliance checklist.

### 10.3 Insurance and passenger safety

Verify the current application of the Vehicle Insurance Against Third Party Risks framework, including **Proclamation No. 799/2013** and **Council of Ministers Regulation No. 554/2024** on premium tariffs and compensation. Obtain insurer/broker advice on additional cover appropriate to passenger carriage and platform exposure.

Require evidence of:
- Valid compulsory third-party motor insurance for every operating vehicle.
- Any required passenger/occupant, public liability, employer/work injury, cargo or professional/cyber cover relevant to the approved activities.
- Insurer confirmation that the actual commercial passenger use, routes, vehicle classes and platform/contractual model are covered.
- Claims handling, accident reporting, emergency response and incident cooperation procedures.

**Evidence:** current policy schedules/certificates, coverage endorsements, insurer confirmation and claims runbook. Do not rely solely on a generic policy certificate if commercial passenger use is excluded.

### 10.4 Payments and financial services

The platform's Pay service and any collection, holding, wallet, escrow, stored value, payout, split settlement or remittance function are out of scope for this assessment and remain disabled.

Primary framework includes **National Payment System Proclamation No. 718/2011** and National Bank of Ethiopia payment-system/payment-instrument directives, including licensing/authorization rules. The NBE maintains a current payment-system directives register.

Before any payment feature:
- Obtain a written legal determination whether the proposed flow constitutes payment-system operation, payment instrument issuance, money transfer, merchant acquiring, agency or another regulated activity.
- Use an appropriately licensed bank/payment service provider for regulated payment execution.
- Execute provider contracts and confirm settlement, reconciliation, chargeback/dispute, refunds, fraud, AML/CFT and consumer-protection responsibilities.
- Do not hold customer funds, issue stored value, operate a wallet, or perform settlement on behalf of others without the required license/authorization.
- Confirm the provider and exact integration are approved for the intended use case and geography.

**Evidence:** counsel opinion, provider license verification, signed contract, approved funds-flow diagram, reconciliation and dispute/refund test, security assessment. No live payment credentials or transactions are part of A5 readiness assessment.

### 10.5 Electronic transactions, consumer and communications obligations

Review the Electronic Transactions Proclamation No. 1205/2020 and applicable consumer, advertising, contract, electronic-signature, records, communications and tax requirements for the final service model. Verify current amendments and implementing directives rather than relying on a title-only reference.

Before launch, approve:
- Terms of service, passenger booking contract and operator agreement.
- Fare/fee disclosure, cancellation, refund, complaint and dispute rules.
- Electronic notices, evidence/record retention and user acknowledgement.
- Marketing claims, operator identity and service limitations.
- Email/SMS sender compliance, user opt-in/opt-out and provider terms.
- Accessibility and Amharic/English content review.

### Regulatory no-go

No real passenger booking, transport operation, driver/vehicle onboarding, live fare collection, ticket issuance, boarding, route advertising as an available commercial service, or public launch until applicable legal determinations, licenses, insurance and operating controls are evidenced and separately approved.

---

## 11. Required A5 work packages and exit gates

A5 remains an assessment/readiness stage. Work packages below define evidence needed; they do not authorize implementation or production deployment.

| Work package | Required output | Current disposition |
|---|---|---|
| A5.1 Infrastructure | Approved hosting, region, topology, environment isolation, cost/ownership and rollback plan | NOT STARTED / NOT EVIDENCED |
| A5.2 Secrets and key lifecycle | Secrets inventory, KMS/secrets design, key lifecycle, access/rotation/revocation evidence | NOT STARTED / NOT EVIDENCED |
| A5.3 TLS and network | Domain/DNS plan, ingress design, TLS, proxy trust, security headers and scan evidence | NOT STARTED / NOT EVIDENCED |
| A5.4 Backup and recovery | RTO/RPO, backup policy, restore and disaster-recovery test | NOT STARTED / NOT EVIDENCED |
| A5.5 Monitoring and incident response | Observability, alerting, audit, on-call and incident exercise evidence | NOT STARTED / NOT EVIDENCED |
| A5.6 Privacy and operations | RoPA, DPIA, DPO/legal decision, SOPs, support, access and supplier controls | NOT STARTED / NOT EVIDENCED |
| A5.7 Regulatory readiness | Written legal classification, licenses, insurance, tax, payments and regional approvals | NOT STARTED / NOT EVIDENCED |
| A5.8 Final go/no-go assessment | Evidence index, residual risk register, owner approvals and explicit decision | NOT STARTED |

### Mandatory final go/no-go criteria

A future A5 readiness review may recommend production only if all of the following are true:
1. The production runtime has been intentionally designed and separately authorized; current development/test and synthetic-only guards have not been bypassed.
2. All critical/high security and privacy findings are closed or formally risk-accepted by the authorized owner with compensating controls.
3. Infrastructure, secrets, TLS, backup/restore, monitoring and incident-response controls have passing production-equivalent evidence.
4. Privacy governance, DPIA/RoPA, notices, rights handling, processor contracts and cross-border decisions are complete.
5. Corporate, tax, transport, insurance, consumer and payment legal requirements are determined and evidenced for the exact service scope.
6. Support, safety, operator verification, complaints, refund/dispute and business continuity processes are staffed and tested.
7. A bounded pilot scope, service area, operators, vehicles, routes, dates, support hours and rollback/suspension criteria are approved.
8. A written owner decision separately authorizes the next implementation/release/deployment stage.

A single unresolved critical legal, safety, privacy, key-management, backup or access-control issue is a no-go.

---

## 12. Owner decisions required later (not requested by this assessment)

The following decisions are deliberately left open:
- Hosting provider and jurisdiction/region.
- Data residency and cross-border vendor policy.
- Whether the platform will contract directly with passengers, operators, or both.
- Regulatory classification of MaaleNex's role and required license(s).
- Pilot operator(s), vehicle classes, routes, terminals and operating geography.
- Payment model and licensed provider (if/when separately authorized).
- Privacy governance owner/DPO arrangement.
- RTO/RPO, service availability target and support hours.
- Budget ceiling and named account/billing owner.
- Pilot go-live criteria and authority to suspend service.

No production provider, paid resource, subscription, domain, certificate, key or license has been selected or purchased by this document.

---

## 13. Explicit exclusions and safety boundaries

This assessment has not:
- Created or configured production infrastructure, accounts, databases, DNS, certificates, secrets or encryption keys.
- Changed application runtime guards or disabled synthetic-only mode.
- Deployed code, merged PRs, changed the default branch or published a release.
- Enabled real passenger/operator accounts, personal-data processing, live GPS or location tracking.
- Sent email/SMS, connected payment providers, moved funds or activated Pay.
- Issued travel tickets, enabled boarding or started commercial transport.
- Obtained legal advice, licenses, insurance, regulator approvals or tax determinations.
- Performed an independent penetration test, CodeQL analysis or production security audit.

A5 assessment is **NON-DEPLOYMENT**. PR merges, production configuration, live-data processing, pilot launch and deployment each remain separately gated by explicit Owner authorization.

---

## 14. Official legal and regulatory reference register

The links below are starting points for verification, not a substitute for reviewing the complete current instruments and obtaining advice for the actual business model.

1. Ministry of Justice — [Personal Data Protection Proclamation No. 1321/2024](https://justice.gov.et/en/law/personal-data-protection-proclamation/). The ECA also maintains a [PDP proclamation text portal](https://pdp.eca.et/pdp-proclamation).
2. Ministry of Justice — [Road Transport Proclamation No. 1274/2022](https://justice.gov.et/en/law/road-transport-proclamation/).
3. Ministry of Justice — [Commercial Road Public Transport Operators’ Organizational, Competency Assurance Licensing and Trip Implementation (Amendment) Directive No. 1136/2026](https://justice.gov.et/en/directives/commercial-road-public-transport-operators-organizational-competency-assurance-licensing-and-trip-implementation-amendment-directive/).
4. Ministry of Justice — [Licensing and Authorization of Payment System Operators, Directive No. 313/2020](https://justice.gov.et/am/directives/licensing-and-authorization-of-payment-system-operators-directive-no-313-2020/).
5. National Bank of Ethiopia — [Payment System directives register](https://nbe.gov.et/directives/poyment-system/).
6. Ministry of Transport and Logistics — [Transport laws and resources](https://motl.gov.et/resource_types/transport-law-1).
7. Ministry of Trade and Regional Integration — [Proclamations/resources, including Electronic Transaction Proclamation No. 1205/2020](https://motri.gov.et/en/resource_types/proclamations).
8. Federal Negarit Gazette / Ministry of Transport source — [Vehicle Insurance Policy Against Third Party Risks Premium Tariff and Compensation Fee Regulation No. 554/2024](https://www.motl.gov.et/sites/default/files/resource/%E1%8A%A0%E1%8B%B2%E1%88%B1_%E1%8B%A8%E1%88%B6%E1%88%B5%E1%89%B0%E1%8A%9B_%E1%88%88%E1%8C%88%E1%8A%95_%E1%8B%A8%E1%8A%AB%E1%88%B3_%E1%8A%AD%E1%8D%8D%E1%8B%AB_%E1%8A%A0%E1%8B%8B%E1%8C%85.pdf).

---

## 15. Assessment conclusion

**A5 deployment readiness: NOT READY.**  
**Production infrastructure: NOT EVIDENCED.**  
**Production runtime: BLOCKED by deliberate development/test and synthetic-only safeguards.**  
**Secrets, TLS, backups, monitoring and operational controls: NOT EVIDENCED.**  
**Privacy and regulatory readiness: NOT READY; formal legal and compliance work is required.**  
**Deployment, merge, production activation and public launch: NOT AUTHORIZED.**

The correct next activity is evidence collection and owner-approved readiness work-package planning, not deployment. The current application safety guards must remain in force until a separately authorized production architecture and migration plan exists.


---

## A5.3 follow-on — infrastructure, secrets/key lifecycle and TLS

The detailed repository-backed assessment is recorded in [MAALENEX-A5-3-INFRASTRUCTURE-SECRETS-TLS-ASSESSMENT.md](MAALENEX-A5-3-INFRASTRUCTURE-SECRETS-TLS-ASSESSMENT.md).

**A5.3 disposition: PARTIAL assessment complete; production readiness remains NOT READY.**

Key findings:
- No production hosting topology, infrastructure-as-code, provider/account ownership, data-residency or private-network evidence is present in the inspected repository.
- The current application deliberately rejects non-development/test environments, requires synthetic-only mode and restricts PostgreSQL to local `maalenex_dev`. Preserve these controls; do not bypass them.
- Identity identifier encryption uses AES-GCM and lookup uses HMAC with separate environment settings, but production secret storage, key-version metadata, encryption-key rotation, lookup-key re-indexing, recovery and revocation procedures are not evidenced.
- Cookie Secure behavior depends on explicit configuration or the ASGI request scheme. A TLS-terminating proxy contract, trusted-proxy allowlist and production cookie verification are not evidenced.
- SMTP uses standard TLS verification when TLS is selected, but the configuration currently permits both STARTTLS and implicit SSL to be disabled while email delivery is enabled. This is a fail-closed hardening item for a separately authorized implementation increment.
- CORS defaults to localhost; production CORS, DNS, certificates, ingress hardening and external TLS scan evidence are absent.

No provider was provisioned, no DNS/certificate was changed, no production key was generated or rotated, no SMTP connection/email was sent, and no production deployment or activation occurred.


### A5.3.1 — architecture and network-security design

The provider-neutral architecture, trust-boundary diagrams, data-flow map, environment-separation model, provider-selection criteria and network-security specification are recorded in [MAALENEX-A5-3-1-ARCHITECTURE-TRUST-BOUNDARIES-DATA-FLOWS-NETWORK-SECURITY.md](MAALENEX-A5-3-1-ARCHITECTURE-TRUST-BOUNDARIES-DATA-FLOWS-NETWORK-SECURITY.md).

**Disposition:** Documentation prepared; Owner review pending. No provider, purchase, provisioning, production credentials, DNS/certificate change or deployment is authorized or performed. Existing synthetic-only and development/test runtime guards remain unchanged. Overall A5 remains **NOT READY**.


### A5.3.2 — versioned encryption and lookup-key lifecycle

The design for versioned AES-GCM ciphertext envelopes, key-ID resolution, encryption-key rotation and backfill, HMAC lookup-key dual-index migration, rollback, recovery, revocation and synthetic verification is recorded in [MAALENEX-A5-3-2-VERSIONED-KEY-LIFECYCLE-DESIGN.md](MAALENEX-A5-3-2-VERSIONED-KEY-LIFECYCLE-DESIGN.md).

**Disposition:** Design prepared; Owner review pending. No key material was generated or changed, and no application code, schema, workflow, provider account, infrastructure, DNS, certificate or runtime configuration was modified. Existing synthetic-only and development/test guards remain binding. Overall A5 remains **NOT READY / NO-GO**.


### A5.3.3 — TLS termination, trusted-proxy, cookie, CORS and ingress contract

The provider-neutral security contract is recorded in [MAALENEX-A5-3-3-TLS-PROXY-COOKIE-CORS-INGRESS-SECURITY-CONTRACT.md](MAALENEX-A5-3-3-TLS-PROXY-COOKIE-CORS-INGRESS-SECURITY-CONTRACT.md). It defines the target TLS termination boundary, exact trusted-proxy peers and sanitized forwarding metadata, canonical host/scheme validation, secure session and CSRF cookie requirements, exact credentialed CORS allowlists, ingress/network protections, operational runbooks and future synthetic-only verification cases.

**Disposition:** Contract prepared; Owner review pending; no implementation or live verification performed. No DNS, certificates, runtime configuration, application code, secrets, infrastructure, network resources or workflows changed. Existing development/test-only, synthetic-only and local `maalenex_dev` guards remain unchanged. No merge, deployment or production activation occurred. Overall A5 remains **NOT READY / NO-GO**.


### A5.3.3 — Owner approval and A5.3.4 implementation

The TLS termination, trusted-proxy, cookie, CORS and ingress contract is **OWNER-APPROVED**. The approval authorizes the separately scoped A5.3.4 application configuration hardening and synthetic regression tests; it does not authorize production provisioning, DNS/certificate changes, merge or deployment.

A5.3.4 implementation is isolated on [PR #11](https://github.com/akefadaka-git/maalenex-moto/pull/11), branch `a5/a5-3-4-edge-security-hardening`. Its implementation report is [MAALENEX-A5-3-4-EDGE-SECURITY-IMPLEMENTATION-REPORT.md](https://github.com/akefadaka-git/maalenex-moto/blob/a5/a5-3-4-edge-security-hardening/docs/verification/MAALENEX-A5-3-4-EDGE-SECURITY-IMPLEMENTATION-REPORT.md).

**A5.3.4 status:** Implemented on isolated branch; isolated synthetic unit suite passed 23 tests; exact-HEAD GitHub Actions run [#42568481664](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42568481664) passed on `60ea65e85a6a02e9467ab10ea0970750d49c5376` (70 backend/PostgreSQL tests passed; frontend and security jobs passed).. PR #11 is draft and unmerged. No live proxy, public ingress, DNS, certificates or production runtime controls are claimed as implemented.

All existing development/test-only, synthetic-only and local `maalenex_dev` restrictions remain binding. Overall A5 remains **NOT READY / NO-GO**.

## A5.3.4 focused security review

- Review: [MAALENEX-A5-3-4-FOCUSED-SECURITY-REVIEW.md](MAALENEX-A5-3-4-FOCUSED-SECURITY-REVIEW.md)
- Disposition: **COMPLETED — FINDINGS OPEN**; A5.3.4 is not security-closed pending F-01 through F-03 remediation and exact-HEAD regression tests.
- The 26 admin/operator/catalog/fleet/trip/fare/support mutation handlers and staff/account session revocation routes passed the focused Origin/CSRF route audit. Confirmed open findings: trusted proxy accepts missing HTTPS metadata (P1); proxy client-IP rate-limit collapse (P2); optional Origin on login and guest booking challenge/bootstrap routes (P2); HSTS/CSP remain an unverified production-edge hardening requirement (P2).
- Production readiness remains **NOT READY**. No application-code remediation, deployment, merge or production activation was performed in this review.


## A5.3.4 remediation and exact-HEAD CI update

- **F-01 trusted-proxy HTTPS metadata: VERIFIED-CLOSED** for application behavior; trusted proxy requires exactly one HTTPS forwarded-proto value and fails closed otherwise.
- **F-03 browser Origin enforcement: VERIFIED-CLOSED** for staff/account login, guest challenge bootstrap and cookie-authenticated guest booking mutations; duplicate, missing, malformed and non-allowlisted Origin values are denied.
- **F-02 rate-limit client identity: VERIFIED-CLOSED** for the documented single-hop edge profile; validated X-Forwarded-For is parsed only from a trusted immediate peer, and untrusted peers retain their direct socket identity.
- Exact-HEAD verification: [run #42571302514 — success](https://github.com/akefadaka-git/maalenex-moto/actions/runs/42571302514) on `3bce5b81c91ad9a573a02e55d3a6e2f6da1a3121`; backend/PostgreSQL 82 passed, 1 warning; frontend, dependency, static security and migration gates all passed.
- **F-04 remains OPEN** as a production-edge gate for HSTS/CSP ownership, real TLS termination, ingress/network controls and external verification. No hosting provider or production ingress has been provisioned.
- PR #11 remains a separate draft/unmerged implementation review. No main-branch modification, merge, deployment, production secrets, real data, payment, GPS or commercial activation occurred.

**A5.3.4 application implementation and automated verification: VERIFIED-CLOSED for F-01/F-02/F-03 scope. Overall A5 production readiness remains NOT READY / NO-GO.**


## F-04 production-edge design and acceptance update

- Design package: [A5.3.5 F-04 Production-Edge Security Design and Acceptance](MAALENEX-A5-3-5-F04-PRODUCTION-EDGE-DESIGN-AND-ACCEPTANCE.md).
- HSTS/CSP single owner: public ingress edge. The application retains CORS, Origin/CSRF, cookie and proxy-trust controls; no weakening or duplicate policy ownership.
- HSTS staged rollout and subdomain/preload restrictions defined; CSP report-only observation, enforcement criteria and rollback defined.
- TLS termination, encrypted private origin hop, origin isolation, ingress hardening, external evidence IDs and F04-01 through F04-12 acceptance gates defined.
- **F-04: DESIGN-RESOLVED / OPERATIONAL ACCEPTANCE PENDING.** No provider, DNS, certificate, endpoint or edge has been provisioned; live TLS/HTTP/HSTS/CSP/origin-bypass scans and rollback exercises are NOT RUN.
- Existing APP_ENV development/test restriction, SYNTHETIC_DATA_ONLY requirement and local maalenex_dev database restriction remain unchanged. No production secret, real data, DNS, certificate, network, runtime, merge or deployment change.

**Overall A5 remains NOT READY / NO-GO.**
