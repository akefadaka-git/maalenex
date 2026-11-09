# MaaleNex Moto — Official Administrative Data Request Package

**Document status:** Draft templates for Owner review and submission  
**Prepared:** 2026-11-09  
**Project:** MaaleNex Moto regional geographic coverage baseline  
**Target coverage:** Maale area, South Omo Zone, Ari Zone and the connecting corridors  
**Repository stage:** Design / data acquisition; no production boundary or routing activation

> **Important:** These are draft requests only. They have not been sent, signed, registered or approved by any public authority. Complete the sender's legal identity, address, contact details, date, signature and any required company documentation before submission. Do not imply that MaaleNex Technologies PLC is already incorporated; it is currently in formation.

## 1. Purpose and administrative routing

MaaleNex Moto is preparing a geographic data baseline for a proposed passenger-mobility service. Before using administrative names, codes, boundaries or road data in a commercial application, the project needs current, authoritative records and written permission for the intended uses.

The South Ethiopia Regional State Office of the President currently lists **South Omo Zone (Dimeka)** and **Ari Zone (Jinka)** as separate zones. The Owner has supplied a local administrative-history correction that the division process dates from 2022. Public reporting from 2022 describes the Ari community's demand for separate zonal administration while Ari/Jinka was still reported within South Omo; a 2023 research report says the split was announced in August 2023. The current two-zone structure is therefore used for the geographic data model, while the exact legal effective date is explicitly requested from the competent authority. The regional office's public administration page identifies its headquarters in Wolaita Sodo and publishes a general contact channel. These public pages are routing context only; they do not substitute for signed administrative records or authoritative boundary data.

**Recommended submission sequence**

1. **Regional level:** Submit the regional request to the South Ethiopia Regional State Office of the President, asking it to identify and refer the request to the competent regional office/bureau responsible for administrative structure, boundary records, geospatial data and data licensing.
2. **South Omo Zone:** Submit a separate request to the South Omo Zone Administration for its current zonal roster, subordinate woreda/town and kebele records, boundary data and Maale's current administrative parentage.
3. **Ari Zone:** Submit a separate request to the Ari Zone Administration for its current zonal roster, subordinate woreda/town and kebele records, and boundary data.
4. **Maale:** Submit a separate request to the Maale Woreda Administration for its current official name, administrative parent, kebele roster, local-script names, official codes, boundary data and local verification contact.

Where a recipient does not hold the requested records, ask it to identify the responsible custodian and formally refer the request. Do not assume that the regional land-administration, urban planning, statistics, mapping or local-government office is the custodian until the regional administration confirms it.

## 2. Common information and data specification

Request the following, as applicable to the recipient's jurisdiction.

### A. Current administrative register

- The latest signed/approved administrative hierarchy: region, zone, woreda, town/city administration, kebele and any officially recognized lower-level unit.
- Official names in the relevant local script(s), official English names, approved transliterations and known historical/alternative names.
- Official administrative codes/identifiers, parent-unit identifiers and the effective date of each record.
- A clear indication of each unit's status: active, renamed, merged, split, transferred, dissolved, proposed or otherwise.
- A current list of all subordinate units, including units not represented in older public datasets.
- The official source instrument or decision (proclamation, regulation, council decision, administrative order or other record) supporting changes since the 2020 historical snapshot.
- The specific decision(s) and chronology for the South Omo / Ari division: when the proposal or transition process began (including the reported 2022 milestone), when the decision was approved/announced, the legally effective date, any transitional period, and the date on which administrative functions and boundaries were transferred.
- Confirmation that the current zonal arrangement is **South Omo Zone (Dimeka)** and **Ari Zone (Jinka)**, plus the complete historical-to-current crosswalk for affected woredas, town administrations and kebeles.

### B. Geospatial boundary data

Preferred formats, in order where available:

1. GeoPackage (.gpkg)
2. GeoJSON
3. ESRI Shapefile (all required companion files)
4. KML or another official GIS format, if the above are unavailable

For every file, request:

- Coordinate reference system (CRS), including EPSG code or full CRS definition.
- Data creation/update date, effective date and version.
- Feature identifier and the corresponding official administrative code.
- Attribute/schema description and data dictionary.
- Geometry type, topology/quality notes, known gaps and disputed boundaries.
- Scale/resolution or positional accuracy, where known.
- Source institution, responsible data custodian and citation/metadata record.
- Any limitations, disclaimers or areas where boundaries are indicative rather than legally authoritative.

### C. Change history and reconciliation

- A change log from the 2020 administrative snapshot to the current date.
- Units created, renamed, split, merged, transferred between zones/woredas, or otherwise reclassified.
- Old-to-new code/name crosswalks, with effective dates and source decisions.
- Specific clarification of the historical 'Male' / 'Maale' label and code 070707 found in a 2020 historical dataset: whether it refers to the present Maale Woreda, and if so, the official successor code and boundary. No automatic identity mapping is assumed.
- Specific clarification of the historical South Ari and Gelila (Semen Ari) entries previously listed under South Omo, including their current administrative status and successor units.

### D. Rights and permitted use

Please state explicitly whether the authority owns, controls, or is authorized to license the supplied data. Request written permission or a licence covering each intended use:

- Display in a commercial passenger-mobility application.
- Reproduction and distribution of the administrative names, codes and boundary data.
- Creation and display of derived datasets, simplified geometries, map tiles and route overlays.
- Storage, caching and synchronization on company servers and user devices.
- Offline use and distribution of bounded offline map/data packages.
- Updates, corrections and redistribution of updated versions.
- Attribution wording, notices, links, share-alike conditions and any other obligations.
- Fees, restrictions, expiry, geographic limits, security conditions or required approvals.

If the authority cannot grant these rights, ask it to identify the rights holder and the formal process for obtaining permission. Receipt of a file or public availability must not be treated as permission for commercial reuse.

### E. Verification contact

Request the name/title and official institutional contact of a designated technical focal person who can confirm administrative names and hierarchy, GIS file provenance and version, CRS and schema, official codes, boundary disputes or known inaccuracies, update cadence and change notifications, and data licensing and permission conditions.

## 3. Draft letter — South Ethiopia Regional State Office of the President

**To:** The Head, South Ethiopia Regional State Office of the President  
**Attention:** Office responsible for regional administration / intergovernmental relations; please refer to the competent administrative-boundary and geospatial data custodian  
**Location:** Wolaita Sodo, South Ethiopia Regional State, Ethiopia  
**Subject:** Request for current official administrative register, boundary datasets and commercial-use authorization — Maale, South Omo and Ari

Dear Sir/Madam,

I respectfully request the Regional State's guidance and access to the current official administrative records and geospatial boundary datasets needed to establish a reliable geographic information baseline for MaaleNex Moto, a proposed passenger-mobility technology service being prepared by MaaleNex Technologies PLC (in formation).

The intended geographic coverage includes the Maale area, South Omo Zone, Ari Zone and the corridors connecting these areas. The project must use current, authoritative administrative information and must not rely on outdated or unverified public map layers.

I request that your Office:

1. Identify the regional bureau/office legally or administratively responsible for the current regional, zonal, woreda, town-administration and kebele register, official administrative codes, boundary datasets and data licensing.
2. Provide, or formally refer this request to the custodian of, the latest approved administrative hierarchy and complete subordinate-unit rosters for **South Omo Zone (Dimeka)** and **Ari Zone (Jinka)**, including the current administrative status and parentage of Maale.
3. Provide the official instrument and exact chronology for the division process reported to have begun in 2022: proposal/consultation date, council approval date, announcement date, legal effective date, transition arrangements and actual transfer date of administrative functions/boundaries. Please explain any distinction between the 2022 transition milestone and a later formal effective date.
3. Provide available official boundary datasets for the relevant administrative levels, with CRS, schema, feature identifiers, metadata, effective dates and update history.
4. Provide the official decisions and a change-history/crosswalk explaining changes since the 2020 historical administrative snapshot, including the current identity and code of Maale and the present status of historical South Ari and Semen Ari records.
5. Identify the designated technical and licensing focal persons.
6. Confirm in writing the licence or permission terms for commercial display, derivative datasets, server/device caching, offline use and distribution, including required attribution, fees and restrictions.

The requested data will be used initially for internal assessment and verification. No supplied boundary will be published or used for operational routing until its provenance, currency, technical quality and permitted uses have been confirmed.

If your Office is not the custodian of any requested item, I would appreciate a written referral identifying the responsible institution and its official submission procedure.

Thank you for your consideration and guidance.

Respectfully,

**Name:** [Full legal name of authorized applicant]  
**Organization:** MaaleNex Technologies PLC (in formation)  
**Role:** [Founder / authorized representative — confirm before signing]  
**Postal address:** [Complete address]  
**Telephone:** [Telephone]  
**Email:** [Email]  
**Date:** [Ethiopian Calendar date / Gregorian date]  
**Signature:** [Signature]

## 4. Draft letter — South Omo Zone Administration

**To:** The Head, South Omo Zone Administration  
**Attention:** Office responsible for administration / planning / land or geospatial records; please refer to the official data custodian  
**Subject:** Request for current South Omo administrative roster, Maale status and official boundary data

Dear Sir/Madam,

I respectfully request the current official administrative register and boundary information held by the South Omo Zone Administration for the preparation of a geographic data baseline for MaaleNex Moto, a proposed passenger-mobility technology service.

In particular, please provide or identify the custodian for:

1. The current list of all woredas, town administrations, kebeles and other officially recognized subordinate units within South Omo Zone.
2. Official local-script and English names, approved transliterations, official codes, parent-child relationships and effective dates.
3. The current administrative status and parentage of Maale, including the authoritative current name/code and the full list of subordinate kebeles.
4. Current official boundary files for the zone and subordinate units, preferably GeoPackage, GeoJSON or shapefile, with CRS, schema, feature IDs, metadata and positional-accuracy notes.
5. Change history since the 2020 historical dataset, including the 2022–2023 South Omo/Ari transition and units transferred, renamed, split, merged or newly established. Please clarify the current status of historical records labelled 'Male', 'South Ari (Bako Gazer)' and 'Gelila (Semen Ari)', and provide the official effective dates and successor codes.
6. The official source decisions and the name/contact of the responsible administrative and GIS data custodians.
7. Written permission/licence terms for commercial display, derivative works, caching, offline storage and distribution, including attribution and any restrictions.

If any boundary is disputed, indicative, incomplete or not suitable for navigation, please identify it as such. We will not infer road access, motorcycle suitability or operational service coverage from administrative boundaries.

If these records are maintained by the Regional State or another institution, please identify the responsible office and advise whether this request can be referred.

Respectfully,

**Name:** [Full legal name of authorized applicant]  
**Organization:** MaaleNex Technologies PLC (in formation)  
**Role:** [Authorized role]  
**Postal address:** [Complete address]  
**Telephone:** [Telephone]  
**Email:** [Email]  
**Date:** [Ethiopian Calendar date / Gregorian date]  
**Signature:** [Signature]

## 5. Draft letter — Ari Zone Administration

**To:** The Head, Ari Zone Administration  
**Attention:** Office responsible for administration / planning / land or geospatial records; please refer to the official data custodian  
**Subject:** Request for current Ari Zone administrative roster and official boundary data

Dear Sir/Madam,

I respectfully request the current official administrative register and boundary information for Ari Zone to support the preparation of a geographic data baseline for MaaleNex Moto, a proposed passenger-mobility technology service.

The project treats Ari Zone as a separate administrative coverage area and requires the latest records issued or confirmed by the competent authority. Please provide or identify the custodian for:

1. The current approved list of all woredas, city/town administrations, kebeles and other officially recognized subordinate units in Ari Zone.
2. Official names in the relevant local script(s), English names, approved transliterations, official codes, parent-child relationships and effective dates.
3. Current official boundary files for the zone and subordinate units, preferably GeoPackage, GeoJSON or shapefile, with CRS, schema, feature IDs, metadata and positional-accuracy notes.
4. A change history and official crosswalk explaining the transition from older records that placed South Ari and Semen Ari-labelled units within the historical South Omo Zone, including the reported 2022 start of restructuring, any 2023 approval/announcement, the legally effective date, current names, codes, parentage and effective dates.
5. Any official boundary decisions, administrative instruments or council records that establish the current zonal and subordinate-unit structure.
6. The responsible administrative and GIS data custodians and their official institutional contacts.
7. Written permission/licence terms for commercial display, derivative works, caching, offline storage and distribution, including attribution, fees and restrictions.

Please distinguish official boundaries from indicative planning layers and identify any disputed or unverified areas. The project will not use administrative polygons as proof of road access or motorcycle route suitability.

If the requested data is held by a regional bureau or another authority, please identify the custodian and advise the appropriate referral process.

Respectfully,

**Name:** [Full legal name of authorized applicant]  
**Organization:** MaaleNex Technologies PLC (in formation)  
**Role:** [Authorized role]  
**Postal address:** [Complete address]  
**Telephone:** [Telephone]  
**Email:** [Email]  
**Date:** [Ethiopian Calendar date / Gregorian date]  
**Signature:** [Signature]

## 6. Draft letter — Maale Woreda Administration

**To:** The Head, Maale Woreda Administration  
**Attention:** Woreda administrative affairs / planning / relevant kebele and land/geospatial records office  
**Subject:** Request to verify Maale's official administrative identity, kebele register and boundary data

Dear Sir/Madam,

I respectfully request the Maale Woreda Administration's assistance in verifying the current official administrative identity and geographic records of Maale for a proposed passenger-mobility technology service being prepared by MaaleNex Technologies PLC (in formation).

The project previously identified a historical 2020 administrative dataset containing a record labelled 'Male' with code 070707. This is treated only as a historical candidate and has not been assumed to identify the current Maale Woreda. I therefore request authoritative local confirmation of:

1. Maale's current official name in the relevant local script and English, approved transliteration, official administrative code and current parent zone/region.
2. The complete current list of kebeles and any other officially recognized subordinate units, with local-script names, English names, official codes and effective dates.
3. Current official boundary files for Maale and its kebeles, preferably GeoPackage, GeoJSON or shapefile, with CRS, schema, feature IDs, metadata and positional-accuracy notes.
4. Any changes since 2020, including name changes, boundary adjustments, kebele creation/merger/split, or changes in parent administrative unit; please provide the supporting official decisions where available.
5. Locally recognized settlement names and spelling/transliteration variants that the administration is willing to confirm for a public-facing geographic gazetteer.
6. The designated local administrative and technical focal persons who can support field verification of settlement identity and access points.
7. Written permission/licence terms for commercial display, derived data, caching, offline use and distribution of any supplied records or maps, including attribution and restrictions.

If official boundary files are not held at woreda level, please identify the responsible zonal or regional office and advise how the Woreda can confirm the relevant records.

The project will use this information for controlled internal verification first. It will not treat an administrative boundary as proof that a road is open, passable or suitable for motorcycles.

Respectfully,

**Name:** [Full legal name of authorized applicant]  
**Organization:** MaaleNex Technologies PLC (in formation)  
**Role:** [Authorized role]  
**Postal address:** [Complete address]  
**Telephone:** [Telephone]  
**Email:** [Email]  
**Date:** [Ethiopian Calendar date / Gregorian date]  
**Signature:** [Signature]

## 7. Submission checklist and evidence log

Complete this checklist for each recipient independently.

| Item | Required evidence | Status |
|---|---|---|
| Applicant identity and legal capacity | Confirmed name, role and supporting documents | NOT STARTED |
| Correct recipient and official submission channel | Confirmed by official directory or direct authority confirmation | NOT STARTED |
| Final letter approved and signed | Owner-approved final copy | NOT STARTED |
| Submission evidence | Stamped receipt, official email acknowledgement or registry number | NOT STARTED |
| Response and data receipt | Original response, files and metadata preserved | NOT STARTED |
| Source integrity | Original file hashes (SHA-256), receipt date and source custodian recorded | NOT STARTED |
| Technical validation | CRS, schema, geometry validity, topology and identifiers checked | NOT STARTED |
| Administrative reconciliation | Current hierarchy and historical crosswalk confirmed | NOT STARTED |
| Rights clearance | Written commercial, derivative, caching and offline permissions reviewed | NOT STARTED |
| Field validation | Local authority/operator confirmation recorded | NOT STARTED |
| Owner acceptance | Explicit acceptance before any production integration | NOT STARTED |

### Suggested evidence folder structure

    docs/maps/authority-responses/
      README.md
      regional/
        request/
        acknowledgement/
        source-files/
        licence/
      south-omo/
        request/
        acknowledgement/
        source-files/
        licence/
      ari/
        request/
        acknowledgement/
        source-files/
        licence/
      maale/
        request/
        acknowledgement/
        source-files/
        licence/

Do not commit confidential personal information, private correspondence, or restricted government data to a public repository. Keep originals in an appropriately access-controlled location; publish only approved metadata, non-sensitive evidence references and legally distributable data.

## 8. Current public routing references (checked 2026-11-09)

1. South Ethiopia Regional State Office of the President — Administration: https://www.southethiopiarspo.gov.et/adminstration/  
   Lists South Omo Zone and Ari Zone separately. Public general contact shown on the site: phone **0983989625** and email **info@southethiopirspo.gov.et**. The website host spelling and published email domain differ; verify the email address by telephone or through the official contact page before sending sensitive or formal material.
2. South Ethiopia Regional State Office of the President — Contact: https://www.southethiopiarspo.gov.et/contact/  
   Lists the regional office location as Wolaita Sodo and its general contact details.
3. South Ethiopia Tourism Bureau — Ari Zone overview: https://setourismbureau.gov.et/ari-zone-tourist-destination/  
   Describes Ari Zone as a distinct zone and Jinka as its administrative centre. This is contextual government-published information, not the required official administrative register.
4. South Ethiopia Regional State Office of the President — Overview: https://www.southethiopiarspo.gov.et/overview/

No direct official email or postal address for the South Omo Zone Administration, Ari Zone Administration or Maale Woreda Administration has been verified in this package. Do not invent or guess those contacts. Obtain them through the regional office or an official government directory before submission.

## 9. Data-governance decision

Until the requested authoritative records and written permissions are received and reviewed:

- Keep MAP_PROVIDER_MODE = "schematic".
- Do not publish candidate administrative polygons or use them for routing, dispatch, ETA, fare calculation or service eligibility.
- Do not equate the historical 2020 code 070707 with a current Maale code without official confirmation.
- Do not infer current Ari or South Omo subordinate rosters from the 2020 historical ArcGIS service.
- Do not redistribute government-supplied files unless the written licence expressly permits it.
- Preserve source originals, SHA-256 checksums, metadata, licence text and a record of every transformation.
- Require separate Owner approval before production integration, public release, offline distribution or deployment.

**Exit criteria for this acquisition stage:** current authoritative registers received for all target administrative areas; official hierarchy and change history reconciled; boundary files technically validated; commercial and offline rights documented; local verification completed; and Owner acceptance recorded.
