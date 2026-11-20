# MaaleNex — IROKA Backbone Integration Boundary v1.0

**Status:** Architecture contract only — NOT CONNECTED  
**Owner gate:** A live connector, credentials, endpoint configuration, deployment, or production use requires separate explicit approval.

## 1. Purpose

MaaleNex owns its passenger product, user experience, domain data, safety policy, and operational decisions. IROKA is a separate intelligence foundation. The two systems remain independently deployable and governed.

The frontend must never couple directly to IROKA internals. It calls a MaaleNex-owned typed adapter boundary. A future backend-for-frontend service may validate the caller, apply policy, audit the request, and invoke an authorized IROKA capability.

## 2. Logical structure

    MaaleNex Passenger UI
             |
             v
    MaaleNex UI capability client
             |
             v
    MaaleNex API / policy gateway (future, not enabled)
             |
             +-- Identity and authorization checks
             +-- Consent / data-minimization policy
             +-- Audit and rate limiting
             +-- Locale and calendar context
             |
             v
    IROKA adapter / protocol boundary
             |
             v
    IROKA governed intelligence runtime (separate system)

## 3. Candidate capabilities (not activated)

- language-assistance: Amharic/English explanation and localization assistance.
- journey-information: explain verified, published journey information supplied by MaaleNex; never invent schedules, fares, operators, or availability.
- accessibility-assistance: explain product accessibility features and help users navigate the interface.

Each request must carry a unique request ID, explicit capability, supported locale, and minimum necessary input. Each response must retain request ID, capability, and safety labels for traceability.

## 4. Mandatory controls before live connection

1. IROKA service endpoint and protocol are documented and independently verified.
2. Service identity, mutual authentication, key rotation, revocation, and secret storage are reviewed.
3. MaaleNex API gateway performs authorization, capability allow-listing, rate limiting, audit logging, and input/output validation.
4. User consent, privacy notice, retention, cross-border processing, and data minimization are approved.
5. Amharic language quality, local calendar handling, and passenger-domain factual grounding are tested.
6. Prompt injection, data exfiltration, unsafe recommendations, hallucinated transport claims, and service unavailability are threat-modelled.
7. Timeout, circuit breaker, fallback, observability, incident response, and kill-switch behavior are verified.
8. Owner separately approves activation after independent security and privacy review.

## 5. Fail-closed current state

The current frontend provider returns not-connected and rejects invocation. No endpoint, API key, token, network request, or IROKA runtime is configured. The UI must state this accurately and must not display generated advice as if it came from IROKA.

## 6. Separation of concerns

- MaaleNex remains authoritative for passenger product content, published journey data, user-facing notices, and operational status.
- IROKA does not create or authorize bookings, payments, tickets, fares, routes, or transport operations.
- IROKA cannot bypass MaaleNex authorization, data governance, or Owner approvals.
- No passenger personal data is sent to IROKA by the current implementation.
- IROKA remains a separate project and is not represented as MaaleNex-owned infrastructure.

## 7. Acceptance criteria

- UI builds and runs without an IROKA service.
- The adapter is typed and has no hidden network fallback.
- Disconnected state is visible and unambiguous.
- Calls fail closed with a deterministic error.
- Unit tests verify no connected status is claimed.
- No production endpoint or credential is committed.
