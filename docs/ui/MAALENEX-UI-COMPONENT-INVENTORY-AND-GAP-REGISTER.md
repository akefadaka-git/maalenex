# MaaleNex UI component inventory and gap register

**Baseline:** PR #14 brand/UI branch, before this verification pass.  
**Audience:** product, frontend, Android and acceptance teams.  
**Scope rule:** current frontend is a bilingual synthetic-data prototype. A screen or card marked as a preview is not a live operational capability.

## 1. Existing design-system primitives

| Component | Current implementation | Status / gap |
|---|---|---|
| Button | Primary, secondary, quiet, danger; size, loading, block | Present; confirm keyboard/disabled/loading behaviour in browser and device tests |
| Text field | Label, hint, error, input attributes | Present; no shared select/textarea/phone/OTP/file-upload abstraction |
| Card | Base and interactive style | Present; interactive card semantics need a button/link wrapper |
| Badge | Neutral, success, warning, danger, info | Present |
| Bottom navigation | Responsive navigation primitive | Present; current portal also implements navigation inline |
| Dialog | Native dialog wrapper and close action | Present; verify focus return, Escape and screen-reader announcement |
| Bottom sheet | Dialog-based shell | Present; no drag/gesture contract or tested focus management |
| Skeleton | Text/title loading placeholders | Present |
| Loading indicator | Spinner/status | Present |
| Design tokens | Brand palette, type, spacing, radii, shadows, touch target, light/dark values | Present; theme persistence and contrast audit not evidenced |
| Motion | Reduced-motion CSS overrides | Present |
| Form feedback | Inline notice and basic mismatch check | Ad hoc; no shared field-level validation framework |

## 2. Current screen and flow inventory

### Public / shared
- Welcome / landing page with Amharic and English copy.
- Guest exploration page.
- Sign-in preview and registration preview.
- Help centre, about page and settings page.
- Global header, language switch, top navigation, bottom navigation and footer.
- Ride planner dialog with route selection, route preview, illustrative distance/fare, review and final preview state.

### Passenger
- Guest ride-planner entry point.
- Passenger dashboard preview: profile tile, trip-history placeholder, safety-information placeholder and saved-places placeholder.
- No live trip creation, dispatch, tracking, cancellation, receipts, payments or support integration.

### Driver / operator
- Motorcycle-driver dashboard preview: profile, verification, availability, trip-request and earnings placeholders.
- Heavy-load-driver dashboard preview: profile, verification, capacity, load-request, delivery-history and earnings placeholders.
- Fleet-operator dashboard preview: profile, fleet vehicles, driver roster, assignments and compliance placeholders.
- Registration preview collects role-specific vehicle, plate, licence, load-capacity or organization fields.
- No live onboarding, document review, dispatch acceptance, trip execution, fleet CRUD, payout or compliance workflow.

### Administration
- Restricted administration shell with user management, driver approvals, trip/dispatch oversight, reports, audit/security log and system-configuration tiles.
- Explicit warning that authentication and server-side authorization are not connected.
- No operational admin actions or privilege enforcement in this frontend prototype.

## 3. Required component catalogue (implementation backlog)

| Component family | Required elements | Priority |
|---|---|---|
| Navigation & shell | Authenticated app shell, role-aware nav, breadcrumbs, page header, responsive side nav, offline/sync status | P0 |
| Forms & identity | Select, textarea, phone input, OTP/MFA, password strength, file upload, date/time, address/location autocomplete, validation summary | P0 |
| Feedback | Toast, alert, confirmation dialog, empty/error/offline states, retry, progress, network status | P0 |
| Passenger trip | Pickup/dropoff selector, map pin, fare quote breakdown, vehicle/service selector, booking state timeline, driver/vehicle card, cancel flow, receipt | P0 |
| Driver operations | Availability switch, request card, accept/decline confirmation, navigation handoff, trip state controls, incident/SOS affordance, earnings ledger | P0 |
| Fleet operations | Vehicle and driver tables/cards, assignment queue, compliance expiry status, service-area and operating-hours editor | P1 |
| Administration | Search/filter table, pagination, bulk action with confirmation, role/permission editor, approval queue, audit log viewer, report filters/export | P0 |
| Data display | Data table, metric/KPI card, chart wrapper, timeline, activity feed, document viewer, map legend | P1 |
| Localization & access | Amharic/English locale-aware date/number/currency, accessible icon buttons, RTL-ready layout only if future locales require it, contrast and focus states | P0 |
| Mobile / offline | Safe-area-aware app shell, bottom sheet, offline queue indicator, retry/sync controls, touch target validation | P0 |

## 4. Screen-level gaps

### Passenger
1. Real identity/session lifecycle and account recovery.
2. Accurate service-area and pickup/dropoff selection backed by authoritative geography.
3. Server-calculated fare quote with transparent fees and expiry.
4. Booking creation, dispatch state, driver assignment, live status and cancellation.
5. Trip history, receipts, notifications, complaint/support and emergency flow.
6. Payment integration only after licensing, privacy, security and financial-control gates.

### Motorcycle and heavy-load drivers
1. Secure onboarding, identity/licence/vehicle document capture and review status.
2. Availability, service area, working hours and vehicle capacity.
3. Offer queue with accept/decline and expiry semantics.
4. Trip/load lifecycle, proof of completion and incident reporting.
5. Earnings ledger, adjustments, payout reconciliation and downloadable statements.

### Fleet operators
1. Organization membership and role-based access.
2. Vehicle/driver registry, compliance documents and expiry alerts.
3. Assignment/dispatch board, operational exceptions and service coverage.
4. Fleet utilization, earnings and settlement reconciliation.

### Administration
1. Server-enforced RBAC and privileged-session controls.
2. User/driver/fleet approval queues with evidence and immutable decision history.
3. Service-area, fare-policy and operational configuration with approval workflow.
4. Dispatch oversight, complaints/safety escalation and incident management.
5. Audit events, security monitoring, report export and controlled system settings.

## 5. Acceptance gates

- Amharic-first and English parity across every visible screen, validation message and status.
- WCAG 2.2 AA audit: keyboard, focus, contrast, zoom/reflow, semantics, accessible names and screen-reader flows.
- Mobile acceptance on physical Android devices at narrow widths, safe areas, different launcher/device sizes and low-connectivity conditions.
- All demo/placeholder content remains visibly marked and cannot be mistaken for a live booking, fare, account, payment or administrative action.
- No real personal, passenger, driver, payment or operational data in prototype tests.
- UI acceptance is not complete until API integration, role authorization, privacy and security gates are independently verified.
