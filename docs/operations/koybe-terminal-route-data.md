# Koybe passenger boarding-point data

## Authoritative boarding-point input

The owner confirmed the locally operator-confirmed passenger boarding/terminal pin on 2026-11-22. Store these exact WGS84 coordinates on the canonical `Koybe` location record:

- Latitude: `5.7678630`
- Longitude: `36.7985890`
- Provenance: `operator_confirmed_terminal_pin`

The pin is the Koybe passenger boarding point. It supersedes the earlier exploratory Koybe locality-centre and primary-hospital candidate pins; neither candidate is a terminal substitute.

Migration `0018_koybe_boarding_point` updates the unique existing Koybe location or creates a draft Koybe location if none exists. It creates the named passenger terminal in draft status only when one does not already exist. It fails closed if duplicate Koybe locations or duplicate matching terminal records are found. It does not publish a route, trip, location, or terminal.

## Route geometry verification status

**NOT VERIFIED — do not publish route geometry yet.**

The confirmed pin establishes the boarding-point coordinate only. It does not establish the road path, intermediate stops, destination terminal, operator service corridor, distance, or travel time. No operator-sourced route trace, approved stop sequence, or destination terminal evidence has been supplied in the current project record.

Until the operating passenger carrier supplies or confirms the service route information:
- Keep route geometry null and `geometry_status=not_published`.
- Do not derive production geometry from locality-centre/hospital pins, public routing-engine estimates, or guessed road paths.
- Do not publish an operational route or trip from this boarding-point record alone.
- Reconcile operator-sourced route trace/waypoints and the destination terminal against the confirmed Koybe boarding point, then validate GeoJSON `LineString` coordinate order as `[longitude, latitude]` and geographic bounds before publication.

The staging API hostname and restricted Google Maps JavaScript API key remain independent infrastructure dependencies. This change does not provision either, activate billing, switch map providers, merge PRs, or deploy services.
