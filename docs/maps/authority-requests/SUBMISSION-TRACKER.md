# Administrative Data Acquisition — Submission Tracker

**Status at creation:** NOT SUBMITTED  
**Last reviewed:** 2026-11-09  
**Owner approval to submit:** NOT GRANTED / NOT RECORDED

## Recipient register

| Recipient | Draft letter | Official channel verified | Owner-approved / signed | Submitted | Receipt / reference | Response |
|---|---|---|---|---|---|---|
| South Ethiopia Regional State Office of the President | [01](./01-regional-administration.md) | PARTIAL — public phone listed; verify email spelling | NOT STARTED | NOT SUBMITTED | MISSING | PENDING |
| South Omo Zone Administration | [02](./02-south-omo-zone.md) | MISSING | NOT STARTED | NOT SUBMITTED | MISSING | PENDING |
| Ari Zone Administration | [03](./03-ari-zone.md) | MISSING | NOT STARTED | NOT SUBMITTED | MISSING | PENDING |
| Maale Woreda Administration | [04](./04-maale-woreda.md) | MISSING | NOT STARTED | NOT SUBMITTED | MISSING | PENDING |

## Evidence log

For each recipient, record:

- Official institution name and verified submission channel.
- Applicant's final legal name, authority/capacity and supporting documents.
- Final signed request version and SHA-256.
- Submission date/time and method.
- Stamped receipt, registry number or official email acknowledgement.
- Named responding official and official contact.
- Original response and source files, receipt timestamp and SHA-256.
- Licence/permission instrument and exact permitted uses.
- Administrative decision(s), dates and old-to-new unit crosswalk.
- Owner acceptance or rejection.

## Returned-data acceptance checklist

| Gate | Required evidence | Status |
|---|---|---|
| Current administrative hierarchy | Signed/official region-zone-woreda-town-kebele register | NOT RECEIVED |
| South Omo / Ari transition | Decision, approval, announcement and legal effective dates | NOT RECEIVED |
| Maale identity | Current official name, code, parent zone and kebele roster | NOT RECEIVED |
| Boundary data | Official files, CRS, schema, feature IDs, version and metadata | NOT RECEIVED |
| Historical crosswalk | 2020 labels/codes mapped only with authority evidence | NOT RECEIVED |
| Data rights | Written commercial display, derivative, caching and offline permissions | NOT RECEIVED |
| Technical validation | SHA-256, geometry validity, topology, CRS and identifier checks | NOT RUN |
| Field verification | Local administration/operator confirmation | NOT RUN |
| Owner acceptance | Explicit recorded approval before product integration | NOT APPROVED |

## Non-negotiable release controls

- A file received from an authority is not automatically licensed for commercial reuse.
- A boundary polygon is not proof of a road, road access or motorcycle suitability.
- Historical 2020 codes are not current identifiers without an authoritative crosswalk.
- No candidate data may activate production map, routing, dispatch, ETA, fare calculation or offline distribution.
- Keep `MAP_PROVIDER_MODE = "schematic"` until separate data, safety, rights and Owner approval gates pass.

## Event log

| Date | Event | Evidence |
|---|---|---|
| 2026-11-09 | Draft package separated into four recipient-specific letters and a controlled tracker | Git commit to be recorded after verification |
