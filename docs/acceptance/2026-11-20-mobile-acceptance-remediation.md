# MaaleNex mobile acceptance findings and remediation baseline

Date: 2026-11-20  
Device reported by Owner: Samsung Galaxy A16, Android 16  
Source: Owner-performed acceptance tests of the installed MaaleNex application.

## Confirmed observations

| Test | Owner observation | Acceptance result |
|---|---|---|
| 1. Launch and splash | App opens in under 2 seconds; splash is brief and lacks full brand, motto and bilingual welcome | Partial |
| 2. Amharic-first experience | Amharic is primary; Ethiopic typography renders excellently but needs a more polished typeface treatment | Pass with refinement |
| 3. Header and navigation | Header basic; navigation works; icons basic; header disappears while scrolling | Partial |
| 4. Dashboard | Basic layout; widgets missing; interactions none; ordinary visual quality | Fail |
| 5.1 Registration | Minimal fields; no validation; submission error; test account creation reported disabled | Fail |
| 5.2 Login | Fields complete; password visibility and recovery missing; submission error | Fail |
| 6. Profile | Profile/avatar partial; edit, account settings, security and logout missing; language switching works | Partial |
| 7. Map | Owner confirmed map is only a placeholder with no functionality | Fail |
| 8. Passenger transport | Journey search, origin/destination, transport/schedules, booking and fare information all missing | Fail |
| 9. Wallet | Screen, balance, deposit and withdrawal/transfer visible only; transaction history and wallet security missing | Fail |
| 10. Help | Help screen visible only; FAQs, contact, submission and tracking missing | Fail |
| 11. Reporting | Report screen, categories, form/attachments, submission and reference confirmation missing | Fail |
| 12. Visual design | Branding, cards and layout good; icons basic; images missing; overall experience poor | Partial |
| 13. Offline/performance | Offline behavior/navigation partial; connectivity recovery missing; startup fast; minor stability issues | Partial |

## Remediation already committed in this branch

- Android splash overlay now displays MaaleNex branding, the provisional product motto “EVERY JOURNEY, CONNECTED.”, and Amharic/English welcome messages.
- Native splash dismissal waits for both WebView content readiness and a minimum five-second presentation; maximum wait remains bounded.
- Sticky header behavior corrected by removing overflow clipping from the application shell and keeping the platform header sticky.
- Dashboard summary cards navigate to wallet, map/journey, and profile screens.
- Login/registration presentation expanded with more complete registration fields, native required/minimum-length constraints, password visibility, and a recovery entry point.
- Profile editing preview and account/security navigation entry points added. Preview edits are explicitly temporary and not represented as server-persisted data.
- Online/offline status and reconnection feedback added. The UI explicitly states that previously unsent changes are not synchronized.
- Automated frontend tests added for dashboard navigation, password visibility/recovery navigation, and temporary profile editing.

## Known gaps not yet resolved

- No passenger self-registration/session API is exposed by the current backend. Existing staff/operator authentication is not appropriate for passenger accounts and must not be reused.
- Profile preview edits are not persisted to a passenger account.
- Password recovery is an entry point only; recovery backend is not connected.
- Map provider, geolocation, destination search, and verified route data remain unimplemented.
- Journey discovery and booking UI/API integration remain incomplete despite backend booking foundations.
- Wallet customer-account API, payment adapters, transaction history and security UI integration remain incomplete. Real-money movement stays disabled.
- Help/FAQ, support ticket submission/tracking and report persistence/attachments remain incomplete.
- Offline cache/queue and safe synchronization remain incomplete.
- Physical-device verification of the new APK remains pending.

## Release and governance boundary

This document is an acceptance baseline, not a production-readiness declaration. The remediation branch and PR remain unmerged. No deployment, release, production financial activation, or external service spend is authorized by these changes. All public-facing identity remains MaaleNex; proprietary internal technology and architecture are not disclosed.
