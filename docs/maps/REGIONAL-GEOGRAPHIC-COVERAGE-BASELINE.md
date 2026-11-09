# MaaleNex Moto — Regional Geographic Coverage Baseline

**Status:** A2 regional scope and source reconnaissance; administrative and geographic acceptance is **UNRESOLVED**.  
**Prepared:** 2026-11-09  
**Scope:** Maale area, all of South Omo Zone, and all of Ari Zone, South Ethiopia Regional State.  
**Operational use:** Not approved for production routing, dispatch, ETA, fare calculation, navigation, or rider-safety decisions.  
**Relationship to pilot baseline:** This document supersedes the *coverage scope* of the Koybe–Jinka pilot baseline; it does not erase the pilot's historical evidence or approve any pilot coordinates.

## 1. Executive decision

MaaleNex Moto's geographic data programme is to be designed for regional expansion, not limited to the Koybe–Jinka corridor.

The initial regional coverage envelope is:

1. **Maale area:** all currently recognized Maale administrative territory, including its kebeles and settlements, subject to current administrative confirmation.
2. **South Omo Zone:** the full zone, all current woredas/town administrations, settlements, service points and inter-woreda road connections.
3. **Ari Zone:** the full zone, all current woredas/town administrations, settlements, service points and connections to South Omo and other adjacent zones.

The regional government's website lists South Omo Zone and Ari Zone as distinct zones. Available South Omo sources place Maale within South Omo as a woreda/district, not as a separate zone. Accordingly, the application data hierarchy must not create a fictional "Maale Zone". Maale is represented as an administrative area under South Omo, with its exact current level and boundaries verified against the latest competent authority record.

**Architecture decision:** adopt a versioned, source-attributed, hierarchical regional gazetteer and road-data pipeline. Keep the frontend's active map mode as `schematic`; no geographic coordinates, road geometry, live map endpoint, or operational routing are activated by this scope document.

## 2. Geographic coverage model

### 2.1 Coverage layers

| Coverage layer | Included scope | Required data |
|---|---|---|
| Regional envelope | South Ethiopia Regional State | Current regional boundary and neighbouring-region interfaces |
| Zone | South Omo Zone | Full zone boundary, current subordinate administrative units |
| Zone | Ari Zone | Full zone boundary, current subordinate administrative units |
| Priority administrative area | Maale | Current administrative parent/level, boundary, all kebeles and settlements |
| Woreda / town administration | Every current unit within South Omo and Ari | Official names, aliases, stable IDs, parent IDs and boundaries |
| Kebele / locality | Every current kebele and named settlement in scope | Boundary or point geometry, source identity and verification state |
| Transport network | Inter-town, inter-woreda, feeder and last-mile links | Road/path geometry, surface, access, restrictions, bridges and seasonal status |
| Mobility destinations | Terminals, markets, health facilities, schools, public offices and other operator-approved stops | Distinct feature type, verified location, opening/access details where relevant |

This is a coverage and data-readiness target. It does not mean every settlement is currently served, every road is connected, or every route is safe for motorcycles.

### 2.2 Administrative naming and hierarchy controls

- Treat **South Omo Zone** and **Ari Zone** as separate administrative coverage branches, based on the regional government's current published zone list.
- Treat **Maale** as a priority area within South Omo, not as a zone, unless a newer authoritative legal/administrative instrument establishes a different status.
- Do not assume that older lists of South Omo woredas remain current after the creation and organization of Ari Zone.
- Do not merge similarly named units or use transliteration as a unique key.
- Preserve official local-script names, English names, historical names, transliteration variants and source-specific spellings as aliases attached to one stable internal identity.
- Keep administrative hierarchy separate from ethnic, cultural, language, service-catchment and transport-market geographies. These are not interchangeable boundaries.
- Record boundary effective dates and source version; support historical boundary versions rather than overwriting them.

### 2.3 Administrative inventory discrepancy

Public sources are not fully harmonized. The South Ethiopia Regional State Office of the President lists South Omo and Ari as separate zones. A South Omo tourism page describes South Omo as six districts/woredas and two town administrations, while research literature predating or spanning administrative restructuring describes ten districts, including South Ari, Woba Ari, North Ari and Baka Dawula Ari. An October 2025 IRC account describes Ari Zone as four woredas: South Ari, Baka Dawla, Woba Ari and Semen Ari.

These records may refer to different administrative dates and boundary arrangements. They must not be combined into one supposedly current woreda list. Obtain a current signed/official administrative roster and boundary dataset from the South Ethiopia regional administration and the respective zonal/woreda offices before assigning definitive parent-child relationships.

## 3. Regional data acquisition plan

### 3.1 Administrative boundaries

Priority source candidates:

1. **South Ethiopia Regional State Office of the President** — current zone nomenclature and administrative announcements. Use as the first source for current published zone naming; request authoritative GIS boundaries and current subordinate-unit rosters directly.
2. **Ethiopian Agriculture Datahub / Ethiopian Administrative Boundary** — lists GeoJSON/WFS, KML and zipped-shapefile resources. The catalogue record states that the original author did not specify a licence. Treat as discovery/inspection material only until rights and provenance are resolved.
3. **Ethiopian Woreda Boundary layer** — catalogue offers GeoJSON/WFS and zipped shapefile, but the listed dataset is dated 2013/2020 metadata and has no licence provided. It is not a current boundary authority without reconciliation.
4. **Ethiopia administrative FeatureServer** — advertises region, zone, woreda and kebele layers. Record service owner, copyright, data date, schema, spatial reference, query limits and reuse rights before extraction.
5. **Open administrative-divisions repository** — a secondary candidate that states CC BY 4.0 and publishes JSON/CSV hierarchy data. It may assist name matching and inventory checks, but is not an authoritative boundary source and its claims must be verified against official records.

For every candidate, capture the exact resource URL, retrieval time, source/version date, data owner, licence, attribution, coordinate reference system, feature count, schema, stable source IDs, geometry validity and checksum. No unlicensed or provenance-unclear boundary dataset may be shipped in the commercial product or offline packs.

### 3.2 Road and path network

- **Leading inspection candidate:** Geofabrik Ethiopia OpenStreetMap extract, preserving OSM object IDs and tags, with ODbL 1.0 review. The country extract is a source input, not a pre-validated local road graph.
- **Ethiopian Roads Administration I-RAMS:** potential authoritative source for federal road segments, functional class, surface type, design standard, bridges, culverts and traffic information. Access, export rights, data freshness, geographic coverage and permitted commercial use remain to be confirmed.
- **Agriculture Datahub road layers:** use only as secondary comparison sources until lineage, age, local coverage and licence are resolved.
- Do not rely solely on main-road datasets for last-mile access. Rural feeder roads, tracks, paths, seasonal crossings and local access constraints must be independently assessed.
- Do not infer motorcycle suitability from OSM highway tags or generic car routing profiles.

### 3.3 Place and service gazetteer

Build a region-wide gazetteer covering settlements, kebeles, markets, bus/minibus terminals, health facilities, schools, public offices, tourism destinations, fuel/service points and operator-approved pickup/drop-off locations.

Keep distinct feature types separate. A hospital point is not a settlement centroid; a town label is not a bus terminal; an administrative seat is not automatically an approved pickup point.

## 4. Proposed data model

Every administrative, place and transport feature must support:

- `id`: stable MaaleNex internal identifier, never derived solely from a mutable name.
- `feature_type`: region, zone, woreda, town administration, kebele, settlement, facility, terminal, road, path, bridge, crossing, pickup point, etc.
- `parent_id`: version-aware administrative parent where applicable.
- `names`: local-script official name, English name, transliteration and source aliases.
- `geometry`: WGS 84 point, line or polygon as appropriate; retain original source CRS and transformation metadata.
- `source`: publisher, source URL, source feature ID, source version/date and licence.
- `integrity`: retrieval timestamp, source-file SHA-256, feature-level provenance and transformation history.
- `verification`: provisional / verified / rejected; method, evidence, verifier role, verification timestamp and confidence.
- `validity`: effective-from, effective-to, last-reviewed and review-due dates.
- `access`: supported modes, restrictions, surface, seasonal conditions, barriers and confidence where evidence exists.
- `publication`: internal-only / review / approved-for-display / approved-for-routing, with explicit approver and approval record.

Administrative identity, geographic geometry, service availability and route suitability are separate approval dimensions.

## 5. Field validation and acceptance

### 5.1 Administrative verification
- Obtain the current South Omo and Ari zone administrative rosters and boundary records from competent regional/zonal authorities.
- Confirm Maale's current administrative level, parent zone, woreda boundaries, kebele list and local-script spellings.
- Reconcile boundary changes and town-administration status with effective dates.
- Record contested, disputed or uncertain boundaries as unresolved; do not silently draw authoritative-looking lines.

### 5.2 Place verification
- Verify settlement and service-point names with local administration and operators.
- Capture field GPS with timestamp, accuracy estimate, collector role and explicit confirmation.
- Obtain separate points for settlement centres, terminals and approved pickup/drop-off places.
- Provide an accessible correction process for local-language name variants and misplaced points.

### 5.3 Road and motorcycle validation
- Inspect the full network across both zones and the Maale area, not only the Koybe–Jinka corridor.
- Check graph connectivity, dangling segments, bridges, river crossings, ferries, one-way restrictions, private roads, access restrictions and surface classifications.
- Validate important inter-town corridors and last-mile feeder links with local operators.
- Record dry-season and rainy-season access separately where conditions differ.
- Mark uncertain links as unverified or unavailable. Never bridge missing roads with straight lines.
- Require motorcycle-specific operator/field assessment before a segment is offered as a motorcycle route.

### 5.4 Operational release
A place may be displayed before it is routable, but it must be labelled according to its evidence state. A road may be included in a research layer without being enabled for dispatch. Production routing requires a separate acceptance record covering data rights, local field validation, safety, privacy, fallback, monitoring and rollback.

## 6. Coverage rollout sequence

| Stage | Geographic scope | Intended output | Gate |
|---|---|---|---|
| R1 | Maale administrative area | Verified administrative hierarchy, kebeles, settlements and priority local roads | Local authority + field evidence |
| R2 | Rest of South Omo Zone | Full administrative inventory, gazetteer and road-network assessment | Zonal/woreda reconciliation |
| R3 | Ari Zone | Full administrative inventory, gazetteer and road-network assessment | Ari Zone roster and field evidence |
| R4 | Cross-zone corridors | Verified links among Maale, South Omo, Ari and adjoining service/market hubs | Operator and road-suitability validation |
| R5 | Operational map readiness | Provider, routing and offline package decision | Separate Owner approval after all evidence gates |

R1–R5 describe a validation sequence, not a promise that each area is immediately serviceable. The map must show unavailable or unverified coverage honestly.

## 7. Privacy, licensing and offline controls

- Device location remains opt-in and must not be uploaded to a provider or backend without a separately approved purpose, notice and data-flow policy.
- No bulk tile downloads or offline pre-seeding from standard OpenStreetMap tile servers.
- OSM-derived data requires ODbL compliance review, attribution and analysis of share-alike obligations for any distributed derivative database.
- Offline packs must use sources whose licences expressly permit the planned commercial/offline use; packages must be bounded, versioned, checksummed and updateable.
- Keep source datasets and GIS processing outputs outside the frontend bundle.
- Do not include personal contributor metadata or unnecessary personal location traces in the geographic dataset.
- Keep the schematic map fallback available whenever network, provider, style, routing or offline resources are unavailable.

## 8. Current gate status

| Gate | Status | Evidence / next requirement |
|---|---|---|
| Regional target expanded beyond Koybe–Jinka | PASS | Owner instruction in current project conversation |
| South Omo and Ari recognized as separate zones in regional source | PARTIAL | Regional government website lists both; obtain current authoritative GIS boundaries |
| Maale correctly modelled as a South Omo area, not an assumed third zone | PARTIAL | South Omo source describes Maale as a district/woreda; confirm current legal/administrative roster |
| Current South Omo woreda/town inventory | UNRESOLVED | Published sources conflict in count and administrative date |
| Current Ari woreda inventory | PARTIAL | IRC 2025 source lists four woredas; confirm against current Ari Zone administration |
| Current regional/zone/woreda/kebele boundary files | UNRESOLVED | Candidate services exist; licences and currentness need reconciliation |
| Regional OSM road extract acquired and parsed | NOT RUN | Prior PBF acquisition attempt did not complete |
| I-RAMS road data access and reuse rights | UNRESOLVED | Source discovered; data access/licence review required |
| Region-wide field validation | NOT RUN | Requires local authority/operator coordination and field evidence |
| Motorcycle suitability | NOT VERIFIED | Requires route-segment-level validation |
| Live map/routing activation | BLOCKED | Keep schematic mode |

## 9. Source register

1. South Ethiopia Regional State Office of the President, overview and zone list: https://www.southethiopiarspo.gov.et/overview/
2. South Ethiopia Regional State Office of the President, administration and zone list: https://www.southethiopiarspo.gov.et/adminstration/
3. South Ethiopia Tourism Bureau, South Omo Zone overview and district description: https://setourismbureau.gov.et/south-omo-zone-tourist-destination/
4. IRC, *Scaling up the WASH SDG plan to Semen Ari Woreda: Moving towards zone-wide scale* (17 October 2025): https://www.ircwash.org/news/scaling-wash-sdg-plan-semen-ari-woreda-moving-towards
5. Frontiers in Public Health, South Omo pastoralist and agrarian communities study (2024), useful historical context but not current administrative authority: https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2024.1482208
6. Ethiopian Agriculture Datahub, Ethiopian Administrative Boundary: https://data.moa.gov.et/dataset/ethiopian-administrative-boundary
7. Ethiopian Agriculture Datahub, Ethiopian Woreda Boundary: https://data.moa.gov.et/dataset/ethiopian-woreda-boundary
8. Ethiopia administrative boundaries FeatureServer: https://services8.arcgis.com/oTalEaSXAuyNT7xf/arcgis/rest/services/Ethiopia_AdminBoundaries/FeatureServer
9. Open administrative divisions secondary dataset (claims CC BY 4.0; verify before use): https://github.com/open-admin-data/ethiopia-administrative-divisions
10. Ethiopian Roads Administration I-RAMS overview: https://irams.era.gov.et/about
11. Geofabrik, Ethiopia OpenStreetMap extract and ODbL information: https://download.geofabrik.de/africa/ethiopia.html

## 10. Non-goals and safety boundary

This baseline does not activate a live map provider, routing engine, geocoder, dispatch, ETA, fare calculation, turn-by-turn navigation, offline map download or location upload. No candidate coordinate, boundary or road segment is approved for operational use by this document. Existing ride prototype distances and fares remain illustrative only.

## 11. Administrative source reconciliation — 2026-11-09

### 11.1 Direct inspection of historical ArcGIS administrative service

The ArcGIS REST FeatureServer candidate was inspected at layer level and queried for matching South Omo / Ari / Maale records.

- Service: https://services8.arcgis.com/oTalEaSXAuyNT7xf/arcgis/rest/services/Ethiopia_AdminBoundaries/FeatureServer
- Woreda layer: `/1`; fields include `REGIONNAME`, `ZONENAME`, `WOREDANO_`, `WOREDANAME`.
- Zone layer: `/2`; fields include `ZONENAME`, `Zone`, `Z4ID`.
- Kebele layer: `/0`; fields include `R_NAME`, `Z_NAME`, `W_NAME`, `RK_NAME`, `UK_NAME`, `KK_NAME` and corresponding codes.
- Woreda and kebele layer metadata report last data edit **2020-05-19**. The service is not a current administrative authority for post-2020 boundary changes.
- The service metadata does not provide a clear licence/copyright statement. Do not redistribute or package its geometries until reuse rights are established.

Targeted query URL (woreda attributes only, no geometries):
https://services8.arcgis.com/oTalEaSXAuyNT7xf/arcgis/rest/services/Ethiopia_AdminBoundaries/FeatureServer/1/query?where=ZONENAME%20LIKE%20%27%25Omo%25%27%20OR%20ZONENAME%20LIKE%20%27%25Ari%25%27%20OR%20WOREDANAME%20LIKE%20%27%25Maale%25%27&outFields=REGIONNAME%2CZONENAME%2CWOREDANO_%2CWOREDANAME&returnGeometry=false&f=pjson

The query returned eight records under `REGIONNAME = SNNPR` and `ZONENAME = South Omo`:

| Historical woreda label | Historical code |
|---|---:|
| South Ari (Bako Gazer) | 070702 |
| Selamgo | 070701 |
| Gnangatom | 070708 |
| Bena Tsemay | 070705 |
| Hamer | 070704 |
| Dasenech (Kuraz) | 070706 |
| Gelila (Semen Ari) | 070703 |
| Male | 070707 |

The matching query did **not** return a separate Ari Zone record. The historical data instead places South Ari and Semen Ari-labelled units inside South Omo. This is consistent with an older administrative snapshot, not evidence against the regional government's current listing of Ari Zone as a separate zone. The record labelled `Male` is a candidate historical match for Maale, but the name alone is not sufficient to establish identity or current administrative status.

### 11.2 Reconciliation finding

1. **Historical snapshot only:** the service's 2020 data date predates the present regional and zonal organization. It is useful for tracing legacy names/codes and detecting changes, not for asserting current boundaries.
2. **Ari Zone gap:** the queried service does not model the currently published Ari Zone as a distinct zone. Do not derive Ari's current woreda roster from this layer.
3. **Maale identity:** preserve `Male` / `Maale` as a possible alias relationship requiring local authority confirmation; do not automatically map historical code `070707` to a current Maale administrative ID.
4. **South Omo roster:** the eight returned rows are historical candidates only. Do not treat them as the current South Omo inventory.
5. **Kebele hierarchy:** the layer schema can support historical parent/child tracing, but no current kebele inventory or production geometry has been accepted.
6. **Licence:** no clear service licence was established; metadata inspection is not permission to redistribute the data.

### 11.3 Current status amendment

| Gate | Status | Evidence / next requirement |
|---|---|---|
| Historical South Omo woreda attributes retrieved | PARTIAL | Eight attribute records queried from 2020 service; not current |
| Historical Ari Zone representation | MISSING | No separate Ari Zone returned by targeted query |
| Historical Maale candidate record | PARTIAL | `Male`, code 070707; confirm identity and boundary with authorities |
| Current South Omo roster | UNRESOLVED | Obtain current signed zonal roster and boundary file |
| Current Ari Zone roster | UNRESOLVED | Obtain current Ari Zone administrative roster and boundary file |
| Current Maale administrative parent and kebeles | UNRESOLVED | Obtain Maale / South Omo authority confirmation |
| Historical ArcGIS geometry reuse rights | UNRESOLVED | Service licence/copyright not established |
| Production boundary activation | BLOCKED | No historical layer is accepted as current or licensed |

### 11.4 Next acquisition action

Request the following from the South Ethiopia regional administration, South Omo Zone administration, Ari Zone administration and Maale woreda administration:

- Current administrative roster with local-script and English names, official codes and effective dates.
- Current zone, woreda/town-administration and kebele boundaries in GeoPackage, GeoJSON or shapefile, with CRS stated.
- Signed/official source citation and named data custodian.
- Licence or written permission covering commercial display, derivative works, caching and offline distribution.
- Change history identifying units transferred, renamed, split or newly established since the 2020 snapshot.

Until received and reconciled, use the 2020 records only as historical comparison metadata, never as production boundaries.
