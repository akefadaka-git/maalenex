# Android device acceptance remediation

## Scope
This change addresses the first device report: application launch and Amharic rendering passed; navigation was reported partially functional; location selectors were empty; trip search could not retrieve data; offline behavior was not tested.

## Frontend changes
- Added touch-sized in-app anchor navigation for Home, Find trips, and Help. The brand mark now navigates to the app's home section rather than the root URL.
- Added a Help/test-information section and explicit API-origin diagnostic.
- Routed all frontend API requests, including QR image retrieval, through `VITE_API_BASE_URL`.
- Added online/offline connectivity status indication.
- Preserved the Amharic-first interface and synthetic-only / no-payment / no-ticket / no-boarding boundary.

## API configuration
Set `VITE_API_BASE_URL` at build time to the HTTPS origin of the deployed test API, for example `https://api-test.example.org` (replace with the actual authorized host). Do not set a guessed host. The Vite development proxy is only for local development and is not available in the installed APK.

If the variable is empty in the APK, API requests remain same-origin and cannot reach a separately hosted FastAPI backend. The Help section displays that the API origin is not configured.

## Data dependency
The locations endpoint must return at least two published synthetic locations from `GET /api/v1/catalog/locations`. The trip endpoint must return synthetic trips for `GET /api/v1/trips/search`. An empty location list is a valid empty state; it is not a navigation crash. No production passenger, payment, ticketing, or boarding data may be introduced.

## Offline behavior
The shell remains loaded when connectivity is lost and displays a clear offline indicator. Server-dependent search, booking, and support operations require connectivity. This is not full offline booking or background synchronization.

## Remaining release gates
- Configure a real, approved HTTPS test API origin.
- Verify CORS / cookie / CSRF behavior against that deployed origin.
- Seed and verify synthetic test locations and trips.
- Run Android APK workflow, install the new artifact, and repeat the physical-device test.
- No merge, production deployment, or commercial activation is included.
