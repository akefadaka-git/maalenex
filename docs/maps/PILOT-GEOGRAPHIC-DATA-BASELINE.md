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
