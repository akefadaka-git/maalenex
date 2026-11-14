# MaaleNex Moto — Koybe–Jinka pilot geographic-data baseline

**Status:** A2 source reconnaissance; geographic acceptance is **UNRESOLVED**.  
**Prepared:** 2026-11-09  
**Scope:** Koybe / Maale Woreda / Jinka pilot geography only.  
**Operational use:** Not approved for routing, dispatch, ETA, fare calculation, navigation, or rider safety decisions.

## 1. Executive finding

Publicly discoverable sources identify Koybe as a kebele/locality in Maale Woreda and identify Jinka as a town in the South Ethiopia Regional State. They do not yet provide a single, independently reconciled coordinate for each operational pickup/drop-off centroid, nor a downloaded and inspected road graph for the Koybe–Jinka corridor.

A road-network dataset is listed by the Ethiopian Agriculture Datahub as an Ethiopian road network sourced from OpenStreetMap, with GeoJSON and zipped-shapefile resources. The dataset endpoint could not be inspected during this pass. Its existence is a lead, not proof of current local coverage, legal suitability, route continuity, or motorcycle access.

**Decision:** Keep `MAP_PROVIDER_MODE = "schematic"`. Do not add geographic coordinates or route geometry to application runtime data in this stage.

## 2. Place identity and coordinate evidence register

Coordinates below are **source-reported candidates only**. They are not approved production coordinates.

| Place / feature | Candidate coordinate (lat, lon) | Source identity | Assessment |
|---|---:|---|---|
| Jinka town | 5.7862, 36.5654 | OpenStreetMap node 540265111; `place=town` as surfaced by Mapcarta | Candidate town feature; reconcile with local authority / field GPS before acceptance |
| Jinka village/locality | 5.83195, 36.63193 | OpenStreetMap node 2506805652; `place=village` as surfaced by Mapcarta | Distinct feature and materially different location; do not silently substitute for the town |
| Koybe locality | 5.770312, 36.809271 | ElevationMap locality listing | Secondary gazetteer-style candidate; feature ID and primary source lineage not established |
| Koybe Primary Hospital | 5.77225, 36.79849 | Facility record AF-ET-038934, attributed by Veligraph to Ethiopia's national facility register | Facility point only; not a settlement centroid or pickup point |

### Interpretation

- The two Jinka records are not interchangeable: they have different OSM node IDs and feature classifications.
- The Koybe hospital point is a facility location, not the Koybe settlement centre.
- Straight-line distance between candidate pins is not a road distance and must not be used to validate the existing illustrative route distances.
- No candidate coordinate in this table is currently authorized for app routing or live location snapping.

## 3. Local geographic context

A Dilla University master's thesis on Maale Woreda describes the woreda study area as approximately 5°30′–6°00′ N and 36°43′–37°00′03″ E and identifies Koybe among the sampled kebeles. It also reports road accessibility as a challenge during field data collection. This supports the regional context and the need for field validation; it does not establish current road geometry or the exact Koybe settlement coordinate.

## 4. Road-network data candidate

The Ethiopian Agriculture Datahub catalogue lists an **ETHIOPIAN ROAD NETWORK** dataset with WGS 84 coordinates and OpenStreetMap as its stated source. Listed resource formats include GeoJSON and zipped shapefile, as well as WMS/WFS resources.

Before this dataset can be used, the team must retrieve and record:
1. Exact downloadable resource URL and dataset/version metadata.
2. Licence and permitted commercial/offline redistribution terms for the dataset and its upstream source.
3. Publication/update timestamp and upstream OSM snapshot date, if available.
4. Feature schema and road-class/access attributes.
5. A bounded extract covering Koybe, Maale Woreda and Jinka, with source checksum.
6. Local topology checks for connected segments, bridges, ferries, one-way restrictions, private/access-restricted roads, and missing links.
7. Local operator confirmation of seasonal passability and motorcycle suitability.

The catalogue entry alone does not establish that the corridor is connected or routable.

## 5. Required acceptance procedure

### Place control points
- Obtain a written or otherwise auditable confirmation of the intended Koybe pickup reference point from the local pilot operator / woreda authority.
- Obtain the intended Jinka terminal or pickup reference point from the operator.
- Capture each point with field GPS or a trusted authoritative geospatial source; record device/source, timestamp, accuracy estimate, collector, and confirmation.
- Keep settlement centroid, bus station, hospital, and individual pickup locations as separate feature types.

### Road corridor validation
- Acquire the candidate road dataset and inspect actual road geometries in a GIS tool.
- Compare the candidate Koybe–Jinka path with current local operator knowledge and field observations.
- Record every uncertain or impassable segment; do not bridge gaps with straight lines.
- Test at least dry-season and rainy-season access with local operators where feasible.
- Do not label a generic car route as motorcycle-safe.

### Data model requirements for later implementation
Every accepted place/segment record should carry:
- Stable internal ID and feature type.
- WGS 84 coordinates or geometry.
- Source name, source feature ID, source URL and licence.
- Source snapshot / retrieved timestamp and content checksum.
- Verification method, verifier role, verification timestamp and confidence.
- Access profile and restrictions where supported by evidence.
- Review/expiry date and a clear `verified`, `provisional`, or `rejected` state.

## 6. Current gate status

| Gate | Status | Evidence / next requirement |
|---|---|---|
| Koybe identity as Maale Woreda kebele | PARTIAL | Academic study identifies Koybe among sampled kebeles; confirm current administrative naming locally |
| Koybe operational pickup coordinate | UNRESOLVED | Local operator / authority confirmation and field GPS required |
| Jinka town identity | PARTIAL | Multiple public records; choose exact operational terminal/pickup feature |
| Jinka operational pickup coordinate | UNRESOLVED | Confirm exact feature with local operator and field GPS |
| Ethiopia road dataset discovery | PARTIAL | Datahub catalogue entry found; retrieve actual resource and metadata |
| Koybe–Jinka road geometry | NOT VERIFIED | No road graph downloaded or inspected |
| Motorcycle route suitability | NOT VERIFIED | Requires local operator / field validation |
| Offline data rights and packaging | UNRESOLVED | Dataset licence and redistribution terms not reviewed |
| Live map/routing activation | BLOCKED | Keep schematic mode until all relevant gates pass |

## 7. Source register

1. Ethiopian Agriculture Datahub, *ETHIOPIAN ROAD NETWORK*: https://data.moa.gov.et/dataset/ethiopian-road-network
2. Mapcarta, *Jinka* (OSM node 540265111): https://mapcarta.com/13013178
3. Mapcarta, *Jinka* (OSM node 2506805652): https://mapcarta.com/13031390
4. ElevationMap, *Koybe, Male, South Omo*: https://elevationmap.net/koybe-male-south-omo-et-1011137836
5. Veligraph, *Koybe Primary Hospital* (facility record AF-ET-038934): https://www.veligraph.com/ethiopia/koybe-primary-hospital
6. Anteneh Bussa, Dilla University, *Land Use/Land Cover Changes and Socio-economic Factors Influencing Agroforestry Expansion in Maale Woreda, Southern Ethiopia* (2019): https://nadre.ethernet.edu.et/record/20247/files/Land%20Cover%20Changes%20and%20Socio-economic%20Factors%20Influencing%20Agroforestry%20Expansion%20in%20Maale%20Woreda.pdf

## 8. Non-goals and safety boundary

This baseline does not authorize or implement a live map provider, geocoder, route engine, navigation, dispatch, ETA, fare calculation, offline map download, or location upload. The schematic preview remains the only active map mode. All distances and fares currently shown in the ride prototype remain illustrative samples, not validated geographic or commercial data.


## 9. Follow-up source acquisition review — 2026-11-09

### Preferred inspection source: Geofabrik Ethiopia OSM extract

Geofabrik's official Ethiopia download page lists `ethiopia-latest.osm.pbf`, a 133 MB PBF extract containing OSM data through **2026-11-06T21:21:21Z** at the time of review. The same page identifies OpenStreetMap contributors as the data source and links the data to the Open Database Licence (ODbL 1.0).

- Dataset page: https://download.geofabrik.de/africa/ethiopia.html
- Exact file: https://download.geofabrik.de/africa/ethiopia-latest.osm.pbf
- Format: OSM PBF
- Snapshot timestamp reported by listing: 2026-11-06T21:21:21Z
- Listed size: 133 MB
- Data licence: ODbL 1.0 (review attribution and share-alike obligations before redistribution or derivative database publication)

**Acquisition result in this work session:** the download was attempted but did not complete in the available execution environment. The PBF has therefore **not** been locally parsed, clipped, hashed, or inspected. This is a source-discovery result only, not road-coverage evidence.

### Other national road layers — limitations identified

- The Agriculture Datahub also lists an ERA-sourced *ETHIOPIA ROAD* layer with a 2020 publication reference and no licence specified. Its national bounding box and available GeoJSON/shapefile formats do not establish local freshness or commercial/offline rights.
- A WFP *Ethiopia Road Network (main roads)* catalogue entry describes an OSM-derived main-road extraction and explicitly says streets and pathways are published separately. Its dataset reference date is 2017. It is not a sufficient sole source for local access roads or last-mile pickup validation.

### Updated source-selection decision

1. Use the Geofabrik OSM PBF as the leading **inspection candidate**, subject to ODbL compliance review and successful local acquisition.
2. Do not use the Agriculture Datahub ERA layer or the WFP main-roads layer as a production routing source until their lineage, age, schema, coverage and licence are independently resolved.
3. Do not import a national layer wholesale into the application. Clip a bounded pilot-area working copy, preserve upstream source IDs/tags, record the extract timestamp and SHA-256, and keep the source file outside the frontend bundle.
4. Validate local road continuity and access with field/operator evidence. OSM road classification or a connected graph alone does not prove seasonal passability or motorcycle suitability.

### Gate status amendment

| Gate | Updated status | Evidence / next requirement |
|---|---|---|
| Current OSM national extract identified | PARTIAL | Geofabrik page lists a 2026-11-06 snapshot; successful acquisition and checksum still required |
| OSM PBF locally acquired and parsed | NOT RUN | Download attempt did not complete in this execution environment |
| ODbL obligations identified | PARTIAL | Geofabrik links ODbL 1.0; legal/attribution/share-alike review required |
| Agriculture Datahub ERA layer licence | UNRESOLVED | Catalogue says no licence specified |
| WFP main-road layer suitability | LIMITED | 2017 reference date; streets/pathways are a separate dataset |
| Koybe–Jinka road graph coverage | NOT VERIFIED | Requires bounded extraction and GIS inspection |
| Live map/routing activation | BLOCKED | Schematic mode remains mandatory |

