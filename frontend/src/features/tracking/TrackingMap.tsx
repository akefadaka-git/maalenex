import { useEffect, useRef, useState } from "react";
import maplibregl, { type GeoJSONSource, type Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import "./tracking.css";

type Position = {
  vehicle_id: string;
  latitude: number;
  longitude: number;
  speed_kph: number;
  heading_degrees: number;
  accuracy_meters: number;
  recorded_at: string;
  received_at: string | null;
  source: "installed_vehicle_gps";
};

const styleUrl = "/mitp-map/style.json";

export default function TrackingMap() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [mapState, setMapState] = useState("Loading self-hosted road map…");
  const [trackingState, setTrackingState] = useState("Select a vehicle ID to view its authorized latest position.");
  const [position, setPosition] = useState<Position | null>(null);
  const vehicleId = new URLSearchParams(window.location.search).get("vehicleId");

  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: styleUrl,
      center: [38, 9],
      zoom: 5,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl(), "top-right");
    map.on("load", () => {
      map.addSource("mitp-vehicle-position", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });
      map.addLayer({
        id: "mitp-vehicle-marker",
        type: "circle",
        source: "mitp-vehicle-position",
        paint: {
          "circle-radius": 9,
          "circle-color": "#b45d22",
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 3,
        },
      });
      setMapState("Self-hosted road-map renderer ready");
    });
    map.on("error", () => setMapState("Map data unavailable — check the local Martin/PostGIS service and OSM import."));
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!vehicleId) return;
    let cancelled = false;
    const refresh = async () => {
      try {
        const response = await fetch(
          "/api/v1/tracking/vehicles/" + encodeURIComponent(vehicleId) + "/latest",
          { credentials: "include", headers: { Accept: "application/json" } },
        );
        if (!response.ok) {
          if (!cancelled) setTrackingState(
            response.status === 401 || response.status === 403
              ? "Staff session or tracking.read permission required."
              : response.status === 404
                ? "No accepted vehicle telemetry is available yet."
                : "Tracking API returned HTTP " + response.status + ".",
          );
          return;
        }
        const next = await response.json() as Position;
        if (cancelled) return;
        setPosition(next);
        const ageSeconds = Math.max(0, (Date.now() - Date.parse(next.recorded_at)) / 1000);
        setTrackingState(ageSeconds > 90
          ? "STALE POSITION · last recorded " + Math.floor(ageSeconds) + " seconds ago"
          : "POSITION CURRENT · updated " + Math.floor(ageSeconds) + " seconds ago");
        const source = mapRef.current?.getSource("mitp-vehicle-position") as GeoJSONSource | undefined;
        source?.setData({
          type: "Feature",
          geometry: { type: "Point", coordinates: [next.longitude, next.latitude] },
          properties: { vehicle_id: next.vehicle_id, speed_kph: next.speed_kph },
        });
        mapRef.current?.easeTo({ center: [next.longitude, next.latitude], duration: 500 });
      } catch {
        if (!cancelled) setTrackingState("Tracking API unavailable; no live position is asserted.");
      }
    };
    void refresh();
    const interval = window.setInterval(() => { void refresh(); }, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [vehicleId]);

  return (
    <main className="mitp-map-page">
      <header className="mitp-map-header">
        <a href="/" className="mitp-map-brand">MAALENEX · MITP</a>
        <span>DEVELOPMENT / SYNTHETIC DATA ONLY</span>
      </header>
      <section className="mitp-map-intro">
        <p className="mitp-map-eyebrow">VEHICLE TRACKING PROOF OF CONCEPT</p>
        <h1>MaaleNex Tracking</h1>
        <p>Self-hosted road-map rendering with an authenticated vehicle-position overlay. No external map API key is used.</p>
        <p className="mitp-map-status" role="status">{mapState}</p>
        <p className="mitp-map-status" role="status">{trackingState}</p>
        {position && (
          <dl className="mitp-map-position">
            <div><dt>Vehicle</dt><dd>{position.vehicle_id}</dd></div>
            <div><dt>Speed</dt><dd>{position.speed_kph.toFixed(1)} km/h</dd></div>
            <div><dt>Accuracy</dt><dd>{position.accuracy_meters.toFixed(1)} m</dd></div>
            <div><dt>Recorded</dt><dd>{new Date(position.recorded_at).toLocaleString()}</dd></div>
          </dl>
        )}
        {!vehicleId && <p className="mitp-map-hint">Open this page with <code>?vehicleId=YOUR-VEHICLE-UUID</code> after a synthetic device is registered, assigned and has submitted telemetry.</p>}
      </section>
      <div ref={containerRef} className="mitp-map-canvas" aria-label="Self-hosted road map and vehicle marker" />
      <footer className="mitp-map-footer">
        Map data is served from the local MaaleNex Martin/PostGIS stack. © OpenStreetMap contributors.
        Position access is staff-authorized; this demonstration does not expose public customer tracking.
      </footer>
    </main>
  );
}
