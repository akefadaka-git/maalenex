import { useEffect, useRef, useState } from "react";
import type { PassengerLocation, PassengerRoute } from "./passenger-api";

type Language = "am" | "en";
type Props = {
  locations: PassengerLocation[];
  routes: PassengerRoute[];
  originId: string;
  destinationId: string;
  language: Language;
  onSelectLocation: (id: string) => void;
};
type LngLat = [number, number];
type Bounds = { extend: (point: LngLat) => void; isEmpty: () => boolean };
type Marker = { setLngLat: (point: LngLat) => Marker; addTo: (map: MapInstance) => Marker; remove: () => void; getElement: () => HTMLButtonElement };
type MapInstance = {
  on: (event: string, callback: () => void) => void;
  remove: () => void;
  fitBounds: (bounds: Bounds, options?: Record<string, unknown>) => void;
  addSource: (id: string, source: Record<string, unknown>) => void;
  addLayer: (layer: Record<string, unknown>) => void;
  getStyle: () => { sources?: Record<string, { type?: string; tiles?: string[]; url?: string }> };
  areTilesLoaded: () => boolean;
  zoomIn: () => void;
  easeTo: (options: Record<string, unknown>) => void;
};
type MapLibreModule = {
  Map: new (options: Record<string, unknown>) => MapInstance;
  Marker: new (options?: Record<string, unknown>) => Marker;
  LngLatBounds: new () => Bounds;
};
declare global {
  interface Window {
    __maalenexMapSmoke?: { zoomIn: () => void };
  }
}

const MAP_STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";
const MAPLIBRE_VERSION = "6.11.2";
const MAPLIBRE_MODULE_URL = `https://unpkg.com/maplibre-gl@${MAPLIBRE_VERSION}/dist/maplibre-gl.mjs`;
const MAPLIBRE_CSS_URL = `https://unpkg.com/maplibre-gl@${MAPLIBRE_VERSION}/dist/maplibre-gl.css`;
let mapLibreLoader: () => Promise<MapLibreModule> = async () => {
  // @vite-ignore — MapLibre is pinned to a versioned ESM CDN URL; no API key or bundler dependency.
  const moduleUrl: string = MAPLIBRE_MODULE_URL;
  return await import(/* @vite-ignore */ moduleUrl) as MapLibreModule;
};
let cssPromise: Promise<void> | null = null;

export function setMapLibreLoaderForTests(loader?: () => Promise<MapLibreModule>) {
  mapLibreLoader = loader ?? (async () => {
    const moduleUrl: string = MAPLIBRE_MODULE_URL;
    return await import(/* @vite-ignore */ moduleUrl) as MapLibreModule;
  });
  if (loader) cssPromise = Promise.resolve();
  else cssPromise = null;
}

function loadMapLibreCss(): Promise<void> {
  if (document.querySelector('link[data-maalenex-maplibre-css="true"]')) return Promise.resolve();
  if (cssPromise) return cssPromise;
  cssPromise = new Promise<void>((resolve, reject) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = MAPLIBRE_CSS_URL;
    link.crossOrigin = "anonymous";
    link.dataset.maalenexMaplibreCss = "true";
    link.onload = () => resolve();
    link.onerror = () => { link.remove(); reject(new Error("MapLibre styles could not be loaded.")); };
    document.head.appendChild(link);
  }).catch(error => {
    cssPromise = null;
    throw error;
  });
  return cssPromise!;
}

function validPoint(value: unknown): LngLat | null {
  if (!value || typeof value !== "object") return null;
  const point = value as { latitude?: unknown; longitude?: unknown };
  if (typeof point.latitude !== "number" || typeof point.longitude !== "number" ||
      !Number.isFinite(point.latitude) || !Number.isFinite(point.longitude) ||
      Math.abs(point.latitude) > 90 || Math.abs(point.longitude) > 180) return null;
  return [point.longitude, point.latitude];
}

function geometryPoints(route: PassengerRoute | undefined): LngLat[] {
  if (route?.geometry_status !== "published") return [];
  const coordinates = route?.geometry?.coordinates;
  if (!Array.isArray(coordinates)) return [];
  return coordinates.flatMap(pair =>
    Array.isArray(pair) && pair.length === 2 &&
    pair.every(value => typeof value === "number" && Number.isFinite(value)) &&
    Math.abs(pair[1]) <= 90 && Math.abs(pair[0]) <= 180
      ? [[pair[0], pair[1]] as LngLat]
      : []
  );
}

export function PassengerMapLibre({
  locations, routes, originId, destinationId, language, onSelectLocation,
}: Props) {
  const host = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapInstance | null>(null);
  const selectLocationRef = useRef(onSelectLocation);
  const [status, setStatus] = useState<"loading" | "ready" | "missing-data" | "offline" | "error">("loading");
  const [message, setMessage] = useState("");
  const [gpsMessage, setGpsMessage] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [styleLoaded, setStyleLoaded] = useState(false);
  const [vectorSourceCount, setVectorSourceCount] = useState(0);
  const [vectorTilesLoaded, setVectorTilesLoaded] = useState(false);
  const [markerCount, setMarkerCount] = useState(0);
  const [interactionCount, setInteractionCount] = useState(0);

  const selectedRoute = routes.find(route =>
    route.origin.id === originId && route.destination.id === destinationId
  ) || routes.find(route =>
    route.origin.id === destinationId && route.destination.id === originId
  );
  const routePoints = geometryPoints(selectedRoute);
  useEffect(() => { selectLocationRef.current = onSelectLocation; }, [onSelectLocation]);

  useEffect(() => {
    let active = true;
    let map: MapInstance | null = null;
    let mapStyleReady = false;
    const markers: Marker[] = [];
    const available = locations.map(location => ({ location, point: validPoint(location.coordinates) }))
      .filter((item): item is { location: PassengerLocation; point: LngLat } => item.point !== null);

    if (!navigator.onLine) {
      setStatus("offline");
      setMessage("You are offline. Map tiles and current route information are unavailable.");
      return () => { active = false; };
    }
    if (available.length === 0 && routePoints.length === 0) {
      setStatus("missing-data");
      setMessage("Published locations do not yet contain verified coordinates, and no published route geometry is available. Ask an administrator to publish source-verified map data.");
      return () => { active = false; };
    }

    setStatus("loading");
    setStyleLoaded(false);
    setVectorTilesLoaded(false);
    setMarkerCount(0);
    setInteractionCount(0);
    Promise.all([mapLibreLoader(), loadMapLibreCss()]).then(([libre]) => {
      if (!active || !host.current) return;
      const initial = available[0]?.point ?? routePoints[0];
      map = new libre.Map({
        container: host.current,
        style: MAP_STYLE_URL,
        center: initial,
        zoom: 7,
        attributionControl: true,
        cooperativeGestures: true,
        maxZoom: 18,
      });
      mapRef.current = map;

      const bounds = new libre.LngLatBounds();
      available.forEach(({ location, point }) => {
        bounds.extend(point);
        const element = document.createElement("button");
        element.type = "button";
        element.className = "maalenex-map-marker";
        element.textContent = location.name;
        element.setAttribute("aria-label", `Select ${location.name}`);
        element.title = location.name;
        const marker = new libre.Marker({ element, anchor: "bottom" })
          .setLngLat(point)
          .addTo(map!);
        element.addEventListener("click", () => {
          if (!active) return;
          setSelectedLocation(location.id);
          selectLocationRef.current(location.id);
          setInteractionCount(value => value + 1);
        });
        markers.push(marker);
      });
      setMarkerCount(markers.length);

      if (routePoints.length > 1 && selectedRoute?.geometry_status === "published") {
        map.on("load", () => {
          if (!active || !map) return;
          map.addSource("maalenex-published-route", {
            type: "geojson",
            data: {
              type: "Feature",
              properties: { routeId: selectedRoute.id },
              geometry: { type: "LineString", coordinates: routePoints },
            },
          });
          map.addLayer({
            id: "maalenex-published-route-line",
            type: "line",
            source: "maalenex-published-route",
            paint: { "line-color": "#0b8f68", "line-width": 5, "line-opacity": 0.95 },
          });
        });
      }

      map.on("load", () => {
        if (!active || !map) return;
        const sources = Object.values(map.getStyle().sources ?? {});
        setVectorSourceCount(sources.filter(source =>
          source.type === "vector" && ((source.tiles ?? []).some(tile => tile.includes("tiles.openfreemap.org")) || (source.url ?? "").includes("tiles.openfreemap.org"))
        ).length);
        mapStyleReady = true;
        setStyleLoaded(true);
        if (!bounds.isEmpty()) map.fitBounds(bounds, { padding: 48, maxZoom: 12 });
        setStatus("ready");
        setMessage("");
        if (import.meta.env.VITE_MAP_RUNTIME_SMOKE === "true") {
          window.__maalenexMapSmoke = { zoomIn: () => map?.zoomIn() };
        }
      });
      map.on("idle", () => {
        if (active && map) setVectorTilesLoaded(map.areTilesLoaded());
      });
      map.on("zoomend", () => {
        if (active) setInteractionCount(value => value + 1);
      });
      map.on("error", () => {
        if (active && !mapStyleReady) {
          setStatus("error");
          setMessage("The map style or vector tiles could not be loaded. Check your internet connection and try again.");
        }
      });
    }).catch(error => {
      if (active) {
        setStatus("error");
        setMessage(error instanceof Error ? error.message : "MapLibre could not be initialized.");
      }
    });

    return () => {
      active = false;
      markers.forEach(marker => marker.remove());
      map?.remove();
      mapRef.current = null;
      if (window.__maalenexMapSmoke) delete window.__maalenexMapSmoke;
    };
  }, [locations, routes, originId, destinationId, routePoints.length]);

  const locate = () => {
    setGpsMessage("");
    if (!navigator.geolocation) {
      setGpsMessage("Location is not supported by this WebView.");
      return;
    }
    navigator.geolocation.getCurrentPosition(position => {
      const point = [position.coords.longitude, position.coords.latitude] as LngLat;
      mapRef.current?.easeTo({ center: point, zoom: 14 });
      setGpsMessage("Showing your device location. This is not driver tracking.");
    }, error => {
      setGpsMessage(error.code === 1
        ? "Location permission was denied. You can still select published locations manually."
        : error.code === 2 ? "Your device location is unavailable."
        : "Location request timed out. Try again or choose a location manually.");
    }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
  };

  const am = language === "am";
  return (
    <section
      className="passenger-map"
      data-map-status={status}
      data-map-style-loaded={String(styleLoaded)}
      data-map-vector-source-count={vectorSourceCount}
      data-map-vector-tiles-loaded={String(vectorTilesLoaded)}
      data-map-marker-count={markerCount}
      data-map-interaction-count={interactionCount}
      data-selected-location={selectedLocation}
      aria-label={am ? "የጉዞ ካርታ" : "Passenger journey map"}
    >
      {status === "ready" && (
        <button className="map-gps-action" type="button" onClick={locate}>
          {am ? "አሁን ያለሁበትን አሳይ" : "Use my location"}
        </button>
      )}
      <div className="passenger-map-canvas" ref={host} role="application" aria-label="Passenger map" />
      {status !== "ready" && (
        <div className="map-state" role="status">
          <strong>{status === "loading" ? (am ? "ካርታው በመጫን ላይ…" : "Loading map…")
            : status === "missing-data" ? (am ? "የተረጋገጠ የካርታ መረጃ የለም" : "Verified map data not published")
            : status === "offline" ? (am ? "ከመስመር ውጭ ነዎት" : "Map unavailable offline")
            : (am ? "ካርታ ማግኘት አልተቻለም" : "Map unavailable")}</strong>
          <p>{message}</p>
        </div>
      )}
      {selectedRoute && selectedRoute.geometry_status !== "published" && (
        <div className="map-legend-note" role="status">
          {am ? "የዚህ መስመር የተረጋገጠ ጂኦሜትሪ ገና አልታተመም።"
            : "No verified route geometry is published for this selection; no straight-line route is drawn."}
        </div>
      )}
      {gpsMessage && <div className="map-legend-note" role="status">{gpsMessage}</div>}
      <div className="map-legend-note">
        {am ? "የካርታ ምልክት ላይ ይጫኑ፤ የተመረጠው የመነሻ/መድረሻ ቁልፍ ይወስናል።"
          : "Tap a map marker to assign it to the selected origin or destination field."}
        <span> · Map data © OpenStreetMap contributors · OpenFreeMap</span>
      </div>
    </section>
  );
}
