# MaaleNex Moto — Portal page and role matrix

**Status:** Frontend design prototype. No authentication, authorization, dispatch or account persistence is claimed.

## Public experience

| Page | Purpose | Access |
|---|---|---|
| Warm welcome | Brand introduction, service areas and primary calls to action | Public |
| Guest dashboard | Public service discovery and sample ride planner | Public |
| Login | Sign-in interface with role selection | Public UI; backend integration pending |
| Registration | Passenger, motorcycle driver, heavy-load vehicle driver and fleet operator onboarding | Public UI; backend integration pending |
| Help | Account, passenger, driver, cargo and safety guidance | Public |
| About | Company/product purpose, values and coverage vision | Public |
| Settings | Language, appearance, notification and privacy preferences | Local preview state only |

## Authenticated workspaces (future server-enforced access)

| Role | Dashboard scope | Required future authorization |
|---|---|---|
| Passenger / rider | Profile, booking/cancellation, trip history, wallet top-up/payment, loyalty card/points, referrals, ratings, receipts and exports | Authenticated passenger account; own-wallet and own-trip scope |
| Motorcycle driver | Driver profile, identity/vehicle verification, availability, trip requests, earnings ledger, available/pending balance, cash-out, transaction history and exports | Driver role plus approved identity/vehicle; own earnings and verified payout beneficiary |
| Heavy-load vehicle driver | Cargo capacity, vehicle/document verification, load requests, delivery history and earnings | Heavy-load driver role plus vehicle and permit verification |
| Fleet / transport operator | Fleet vehicles, driver roster, assignments, compliance and organization-scoped owner/driver settlement reports | Approved operator role, scoped fleet ownership and recorded payout allocation agreements |
| Administrator / finance operator | User management, driver approvals, trip/dispatch oversight, fare governance, reconciliation, payout approval, reports, audit and system configuration | Separate identity, least privilege, server-side permissions, MFA, maker-checker controls and audited actions |

## Security boundaries

- Administrator must never be selectable through public registration.
- Hiding an admin link is not authorization. Every privileged API operation must enforce server-side role and permission checks.
- Passenger, motorcycle driver, heavy-load driver and fleet operator data must be scoped to the authenticated subject and tenant/fleet where applicable.
- Driver availability, trip acceptance, earnings, identity checks and vehicle approval are not functional until backend services and audit controls are implemented.
- Login and registration forms in this branch are non-submitting UI prototypes. They must not collect or persist real credentials.
- The dashboard displays no fabricated trip counts, earnings, approval rates, fleet totals or other live operational metrics.
- Language and appearance controls currently change local component state only; durable preferences require a user-preferences API.
- Help contact channels remain unpublished until officially verified.

## Coverage and product scope

The public experience communicates the planned regional coverage: Maale, South Omo Zone (Dimeka) and Ari Zone (Jinka). It does not imply that road geometry, dispatch, legal transport operations or live routing are ready across those regions.

## Acceptance gates before production

1. Integrate secure authentication, account recovery, session management and rate limiting.
2. Define and test role/permission matrix at API and database layers.
3. Implement identity, licence, vehicle, insurance and operator verification workflows.
4. Implement tenant/fleet isolation and audit trails for administrative actions.
5. Connect real trip, dispatch, cargo, payment and notification services only after their separate safety and regulatory gates.
6. Add component, accessibility, responsive/mobile and end-to-end tests.
7. Obtain exact-HEAD CI evidence and independent security review before merge/deployment.

## Financial and booking capabilities — design scope

The expanded product specification is maintained in `docs/product/MAALENEX-PAY-MOBILITY-AND-FARE-SPEC-v1.0.md`. It defines passenger booking/cancellation/rating/referrals, ETB wallet and immutable ledger, driver/vehicle-owner settlement, cash-out, loyalty card/points, transaction exports, jurisdictional fare governance and legal agreements.

**Development remains synthetic-only.** This matrix does not enable real payments, production personal-data processing, live dispatch, or deployment. Wallet value and loyalty points are separate accounting concepts; administrator and finance privileges are never self-registered.
