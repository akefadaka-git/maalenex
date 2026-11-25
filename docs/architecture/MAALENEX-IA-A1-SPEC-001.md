# MAALENEX-IA-A1-SPEC-001
## Platform-wide Invisible Intelligence Architecture

**Document status:** A1 BASELINE — FROZEN  
**Version:** 1.0.0  
**Product:** MaaleNex  
**Intelligence backbone:** IROKA  
**First application:** MaaleNex Maps  
**Initial interface languages:** Amharic and English  
**Geographic priority:** Maale Woreda, Ethiopia  
**Classification:** Internal architecture and governance specification

---

## 1. Purpose

This specification establishes a unified, platform-wide architecture in which IROKA provides intelligence capabilities behind the scenes while MaaleNex remains the product, service identity and user-facing experience.

The architecture applies to all current and future MaaleNex services. It is not a standalone Maps integration or a separate IROKA product.

Maps is the first application through which this architecture will be established, validated and progressively extended to other services.

## 2. Owner architectural decisions

The following decisions constitute the frozen A1 baseline:

1. MaaleNex is the product and primary end-user-facing identity.
2. IROKA is the internal intelligence backbone across MaaleNex.
3. Ordinary users interact with MaaleNex, not a separate IROKA application or branded assistant.
4. IROKA assesses, discovers, reasons, analyzes, predicts, recommends and optimizes.
5. MaaleNex retains ownership of identity, access, business rules, transactions, workflows and execution.
6. IROKA cannot independently authorize payments, change fares, approve operators, modify wallets or execute business mutations.
7. MaaleNex Maps is the first application of this architecture.
8. Maps must provide useful deterministic services even when IROKA is unavailable.
9. Initial user-facing language support is Amharic and English.
10. Maale Woreda is the first geographic coverage priority.
11. Existing MaaleNex repositories, branches and pull requests must be preserved and reconciled rather than replaced with competing implementations.
12. A2, A3, A4 and A5 remain separate authorization gates.

## 3. Product and intelligence boundary

### 3.1 MaaleNex owns

- Product identity and user experience.
- Customer, operator and administrator accounts.
- Authentication, authorization and permissions.
- Tenants, organizations and business relationships.
- Service catalogues and operational workflows.
- Booking, dispatch, orders and reservations.
- Fare policies and pricing rules.
- Wallets, payments, accounting and financial records.
- Operator registration and approval.
- Notifications and customer support.
- Business records, audit trails and regulatory obligations.
- Final execution of authorized business actions.

### 3.2 IROKA provides

- Context assessment and evidence analysis.
- Knowledge discovery and synthesis.
- Geographic and operational reasoning.
- Search relevance and recommendations.
- Forecasting and prediction.
- Optimization and decision support.
- Anomaly and inconsistency detection.
- Data-quality assessment.
- Operational insights and intelligence reports.
- Authorized learning from verified feedback and outcomes.

IROKA outputs are advisory or analytical unless an independently authorized MaaleNex workflow explicitly permits a defined automated action.

### 3.3 User-facing identity

Ordinary user interfaces must not require users to understand IROKA, configure IROKA or interact with a separate IROKA identity.

Users receive MaaleNex functionality and results. Internal technical documentation, security records and authorized administrative audit reports may identify IROKA where necessary.

Legal disclosures concerning automated processing, data usage and consequential decisions must still be provided when required.

## 4. Platform-wide application scope

The architecture applies to these eight service lines:

| Service | Intelligence responsibilities |
|---|---|
| Move | Mobility discovery, journey analysis and recommendations |
| Transit | Route, schedule, demand and operational optimization |
| Delivery | Address intelligence, dispatch and delivery planning |
| Cargo | Logistics, capacity, corridor and transport analysis |
| Market | Product discovery, market intelligence and recommendations |
| Fleet | Fleet utilization, anomaly detection and maintenance insights |
| Business | Business performance, planning and decision support |
| Pay | Transaction-risk signals, financial anomaly analysis and payment intelligence |

These responsibilities do not transfer business authority to IROKA.

Maps provides shared geographic capabilities to services that require location, distance, route, spatial search and geographic analysis.

The service list is an architectural scope baseline, not a declaration that every service has already been implemented or integrated.

## 5. Target architecture

### Layer 1 — MaaleNex Experience

- Public web experience.
- Customer mobile and PWA experience.
- Passenger and transport interfaces.
- Operator and partner interfaces.
- Internal administration and management interfaces.
- Amharic and English localization.

### Layer 2 — MaaleNex Business Platform

- Identity and access management.
- Service-specific business modules.
- Business workflows and rules.
- Booking, dispatch and operational management.
- Financial and transaction services.
- Notifications and communications.
- Audit and reporting.

### Layer 3 — MaaleNex Intelligence Integration

A common, governed integration layer that:

- Accepts authorized intelligence requests.
- Identifies the requesting service and tenant.
- Enforces purpose, permissions and data minimization.
- Constructs versioned request envelopes.
- Applies timeouts, rate limits and circuit breakers.
- Validates returned results.
- Applies confidence and policy thresholds.
- Records request and result audit references.
- Supports deterministic fallback behavior.

### Layer 4 — IROKA Intelligence

IROKA provides:

- Assessment and reasoning.
- Knowledge synthesis.
- Geographic and contextual intelligence.
- Recommendations and optimization.
- Forecasting and predictive analysis.
- Anomaly detection.
- Data-quality and evidence assessment.

IROKA must remain independent of MaaleNex transaction execution.

### Layer 5 — Data and Computation

- MaaleNex operational databases.
- Geographic database and spatial indexes.
- Approved geographic and reference datasets.
- Search and routing engines.
- Tile and map infrastructure.
- Object and document storage.
- Analytics and processing services.
- Approved external information sources.

The intelligence engine does not replace the data systems or deterministic engines that MaaleNex needs to operate.

## 6. Governed intelligence request lifecycle

Every intelligence request must follow this sequence:

1. A MaaleNex service initiates a request.
2. MaaleNex authenticates the requesting context.
3. MaaleNex verifies tenant, permissions, purpose and allowed capabilities.
4. The integration layer collects only necessary evidence and context.
5. IROKA assesses the request and produces a structured result.
6. MaaleNex validates the result, evidence, confidence and policy compliance.
7. MaaleNex determines whether the result can be displayed, used or escalated.
8. Any consequential business action follows the appropriate MaaleNex authorization and approval workflow.
9. MaaleNex records the decision and applicable audit evidence.

Invalid, expired, unauthorized or unverifiable results must fail safely.

## 7. Authority and safety controls

IROKA must not independently:

- Authorize payments or transfers.
- Freeze, debit or credit wallets.
- Set or change fares.
- Approve, suspend or terminate operators.
- Confirm bookings or execute financial transactions.
- Change business ownership or user permissions.
- Publish unverified geographic facts as authoritative.
- Override MaaleNex policies or Owner-governed approval requirements.

For high-impact decisions, MaaleNex must provide appropriate human review and authorization.

Intelligence recommendations must be distinguishable from verified facts, deterministic calculations and approved business decisions.

## 8. First application: MaaleNex Maps

### 8.1 Purpose

Maps establishes the first reusable intelligence application and supplies shared geographic capabilities to other MaaleNex services.

### 8.2 Core capabilities

- Interactive geographic visualization.
- Location search and discovery.
- Geographic entity and facility information.
- Route planning and journey analysis.
- Distance and estimated travel-time calculation.
- Transport and logistics geographic intelligence.
- Geographic data-quality assessment.
- Geographic change and anomaly detection.
- Offline geographic access where technically and legally feasible.
- Authorized geographic administration and reporting.

### 8.3 Geographic priority

Maale Woreda is the initial coverage area.

The geographic data programme must progressively assess:

- Woreda boundary.
- Kebele boundaries and names.
- Settlements and place names.
- Roads, paths and transport corridors.
- Public facilities and service locations.
- Health and education facilities.
- Markets and commercial locations.
- Water resources and other relevant geographic features.
- Verified passenger boarding and destination locations.
- Relevant environmental and infrastructure information.

No missing boundary, place, population, road, facility or route data may be fabricated to create an appearance of completeness.

### 8.4 Geographic evidence classification

Each geographic record must distinguish:

- Verified.
- Officially published but not independently verified.
- Operator-confirmed.
- Community-reported.
- Estimated.
- Inferred.
- Unknown.
- Not yet collected.

Each record should retain source, collection method, date, verification status, confidence, license, access classification and revision history.

### 8.5 Technical direction

The A1 preferred direction is:

- MapLibre for map rendering.
- PostGIS for spatial data management.
- Martin as a candidate self-hosted vector-tile service.
- Open-source and self-hosted-first infrastructure.
- Offline-capable map and data workflows.
- Routing and geocoding engines selected through A2 technical evaluation.

This is a preferred architecture, not a claim that these components are already deployed or fully validated.

Paid external map services must not be mandatory for core platform functionality.

Imagery, map data and third-party datasets require separate license, attribution, availability and reuse assessments.

## 9. IROKA integration contract

The existing MaaleNex–IROKA integration contract, MN-IROKA-IFACE-001, is the starting point for the governed integration.

The target contract should retain or explicitly reconcile:

- Immutable and versioned request envelopes.
- Tenant and requesting-service binding.
- Request identifiers and expiry.
- Capability and policy-version references.
- Input provenance.
- Output schema validation.
- Confidence and evidence metadata.
- Audit receipt references.
- Authentication and trusted-key validation.
- Revocation and rotation procedures.
- Fail-closed behavior.
- Timeout and retry controls.
- Data minimization and privacy controls.

The existing draft integration must not be treated as proof of a production IROKA endpoint, operational trust-root provisioning or completed network integration.

A2 must establish those facts through repository and technical evidence.

## 10. Security, privacy and data governance

The platform must implement:

- Least-privilege access.
- Tenant isolation.
- Service-level capability restrictions.
- Authentication of service-to-service requests.
- Encryption in transit and at rest where supported.
- Secure credential and key management.
- Key rotation and revocation.
- Data minimization and purpose limitation.
- Retention and deletion policies.
- Auditability of intelligence requests and consequential decisions.
- Protection of sensitive geographic and operational data.
- Safe handling of untrusted external and AI-generated information.

Public and internal data access must be enforced at the API, database and spatial-query layers. Hiding a layer in the user interface is not an authorization control.

## 11. Availability and resilience

MaaleNex must remain operational when IROKA is unavailable.

Required behavior includes:

- Deterministic service fallbacks.
- Timeouts and bounded retries.
- Circuit breakers.
- Queueing only where the underlying operation safely supports it.
- Clear distinction between unavailable intelligence and unavailable core service.
- No duplicate financial or business actions during retries.
- Recovery and audit reconciliation after service restoration.

Maps must distinguish unavailable tiles, unavailable routing, unavailable intelligence and missing geographic data rather than presenting them as equivalent failures.

## 12. Localization and accessibility

Initial language scope:

- Amharic.
- English.

The platform should preserve original local place names and source spellings where available, with separately maintained localized display names.

Ethiopian Calendar support and other localization requirements must be handled by the relevant MaaleNex platform conventions when applicable.

Interfaces should be mobile-first, accessible, readable in both languages and usable under constrained connectivity.

## 13. Repository and implementation preservation

Canonical repository: `akefadaka-git/maalenex`.

The existing implementation streams identified during A1 are preserved:

- PR #43 — passenger map and associated geographic contract work.
- PR #44 — governed IROKA integration contract.
- PR #53 — MITP tracking and self-hosted mapping foundation.

These are separate draft implementation streams and must not be treated as merged or production-ready.

A2 must reconcile overlapping map approaches, data models, migrations, branch dependencies, test evidence and integration contracts before implementation scope is approved.

The A1 assessment observed main at:

`1daf201bfb407280604534e28440b9fa83178efb`

This is a historical assessment reference, not a claim that main still has that SHA at the time of later implementation.

No existing implementation should be discarded merely because this specification selects a unified target architecture.

## 14. Non-functional requirements

The architecture must support:

- Mobile-first access.
- Low-bandwidth operation.
- Resilient offline workflows where appropriate.
- Scalable service integration.
- Secure multi-tenant operation.
- Auditable intelligence use.
- Amharic and English localization.
- Extensible service contracts.
- Deterministic core business operations.
- Data provenance and traceability.
- Cost-conscious open-source infrastructure.
- Maintainable and testable components.

Quantitative performance, availability, recovery and capacity targets remain to be established during A2 based on measured constraints and service criticality.

## 15. A1 acceptance criteria

The A1 baseline is complete when the following are established:

1. Platform-wide invisible intelligence principle is explicit.
2. MaaleNex and IROKA responsibilities are separated.
3. All eight service lines are covered by the target architecture.
4. Maps is identified as the first application.
5. The five-layer architecture is documented.
6. The governed intelligence request lifecycle is specified.
7. Business authority and prohibited IROKA actions are documented.
8. Geographic evidence and provenance requirements are defined.
9. Maale Woreda is established as the first geographic priority.
10. Amharic and English are established as initial interface languages.
11. Security, privacy, resilience and audit requirements are specified.
12. Existing repository and PR preservation requirements are documented.
13. A2, A3, A4 and A5 remain separate authorization gates.
14. Unverified technical and operational facts are explicitly identified.

## 16. Deferred decisions

The following are deliberately not frozen as final implementation choices:

- Final routing engine.
- Final geocoding provider.
- Geographic dataset authority and licensing.
- Authoritative Maale Woreda boundary source.
- Complete kebele and settlement inventory.
- Satellite and aerial imagery licensing.
- Production tile hosting topology.
- Offline package distribution and update protocol.
- IROKA production endpoint and trust-root provisioning.
- Performance and availability service-level objectives.
- Production infrastructure sizing and operating costs.
- Final implementation sequencing across existing PRs.

These require A2 read-only reconciliation, evidence and technical evaluation.

## 17. Stage-gated delivery

| Stage | Scope | Authorization |
|---|---|---|
| A1 | Assessment, architecture specification and baseline freeze | This specification |
| A2 | Read-only repository and technical reconciliation | Separate authorization |
| A3 | Approved implementation | Separate authorization |
| A4 | Verification, security and acceptance evidence | Separate authorization |
| A5 | Deployment and production release | Separate authorization |

A1 completion does not authorize implementation, merging, production migration or deployment.

## 18. Baseline change control

This specification is version 1.0.0.

The frozen architectural principles must not be silently rewritten. Future changes require a controlled amendment that records:

- Amendment identifier.
- Reason and supporting evidence.
- Exact affected requirements.
- Impact on existing services and contracts.
- Security and governance implications.
- Owner decision.
- Version and effective date.

A material authoritative contradiction may justify a controlled review. It does not automatically reopen unrelated A1 decisions.

## 19. Final A1 disposition

**MAALENEX-IA-A1-SPEC-001 v1.0.0 — FROZEN**

The platform-wide invisible intelligence architecture is established as the MaaleNex target architecture.

IROKA is the internal intelligence backbone. MaaleNex remains the product and business authority. Maps is the first application, beginning with Maale Woreda and Amharic/English support.

This freeze establishes the architecture and requirements baseline. It does not certify implementation, integration, geographic data completeness, production readiness or deployment.

**Next stage:** Owner authorization of A2 read-only reconciliation.

**No merge, deployment, production migration or A3 implementation is authorized by this A1 specification.**
