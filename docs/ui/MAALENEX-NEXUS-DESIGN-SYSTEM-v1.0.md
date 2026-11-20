# MaaleNex NEXUS Design System v2.0

**Status:** Full-platform UI foundation on an unmerged feature branch.  
**Product direction:** Amharic-first, mobile-first mobility and digital-services platform.

## Visual identity
Deep evergreen and midnight graphite foundations, luminous mint/cyan accents, geometric navigation motifs, restrained motion, and a distinctive abstract MaaleNex emblem. All public surfaces use MaaleNex branding only.

## Core design tokens
- Midnight: #071A1C
- Deep evergreen: #0B2928
- Primary mint: #B5EFCC
- Signal green: #55B98B
- Action mint: #83D9B0
- Warm focus: #F2C27C
- Muted text: #A9BEB4

## Typography and localization
Amharic is the default locale, with English available. Noto Sans Ethiopic is preferred, followed by Noto Sans, Nyala, and system fallbacks. The interface must support Ethiopian calendar presentation, locale-aware dates and numerals, text scaling, and narrow mobile layouts.

## Application shell
- Smart header with brand, notifications, language, and profile access.
- Responsive navigation rail on wider screens and horizontally scrollable navigation on mobile.
- Dashboard with quick actions, wallet status, journey-information status, and account state.
- Dedicated map, wallet, profile, login, registration, help, report, and About views.
- Reusable cards, status pills, forms, transaction rows, empty states, notices, and specialized iconography.

## Functional state and boundaries
This branch currently supplies the first frontend screen foundation. Authentication, persistent profile storage, notifications, maps provider, backend APIs, wallet ledger, payments, deposits, withdrawals, and support transmission are not yet connected. The wallet is explicitly non-transactional; report submission is local demonstration state only. No false route, fare, operator, payment, or transaction claims may be shown.

## Security and financial architecture requirements
- Authentication: server-side identity, secure sessions/tokens, rate limits, recovery, device/session controls, and audit events.
- Wallet: double-entry ledger, immutable journal, idempotent transaction commands, reconciliation, reversals, limits, fraud monitoring, and signed provider callbacks.
- Money movement: only through an appropriately licensed/authorized bank or payment provider; secrets remain server-side.
- KYC/AML, privacy, consumer disclosures, data retention, and regulatory controls must be assessed before real-money activation.
- Map provider keys and user location permissions must be scoped and protected; no fabricated operating routes.
- Independent security review and staged operational approval are mandatory before production activation.

## Accessibility and Android
Maintain visible keyboard focus, semantic controls, reduced-motion behavior, scalable text, and responsive layouts. Android acceptance requires resource compilation, APK assembly, emulator checks, and physical-device verification of launcher and splash behavior. This design system is not an accessibility certification.


## Bundled Amharic font
The frontend bundles Noto Sans Ethiopic from the pinned `@fontsource/noto-sans-ethiopic` 5.3.0 package under the SIL Open Font License 1.1. Font files are served locally from the packaged web assets; no external font CDN is required.
