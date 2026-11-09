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
| Passenger / rider | Profile, trip history, saved places, safety information | Authenticated passenger account |
| Motorcycle driver | Driver profile, identity/vehicle verification, availability, trip requests and earnings | Driver role plus approved identity and vehicle |
| Heavy-load vehicle driver | Cargo capacity, vehicle/document verification, load requests, delivery history and earnings | Heavy-load driver role plus vehicle and permit verification |
| Fleet / transport operator | Fleet vehicles, driver roster, assignments and compliance | Approved operator role and scoped fleet ownership |
| Administrator | User management, driver approvals, trip/dispatch oversight, reports, audit and system configuration | Separate administrator identity, server-side role/permission checks, MFA and audited privileged actions |

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
