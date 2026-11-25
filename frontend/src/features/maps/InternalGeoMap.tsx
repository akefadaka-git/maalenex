import { useEffect, useRef, useState } from "react";
import maplibregl, { type Map as MapLibreMap } from "maplibre-gl";
import type { FeatureCollection, Point } from "geojson";
import "maplibre-gl/dist/maplibre-gl.css";
import "./public-map.css";

type Position = {
  vehicle_id: string;
  longitude: number;
  latitude: number;
  recorded_at: string;
  received_at: string;
  speed_kph: number;
  heading_degrees: number;
  accuracy_meters: number;
  is_synthetic: boolean;
};
type PositionsResponse = { positions: Position[] };
type VehicleFeature = GeoJSON.Feature<Point, {
  vehicle_id: string;
  speed_kph: number;
  heading_degrees: number;
  accuracy_meters: number;
  recorded_at: string;
  is_synthetic: boolean;
}>;
const EMPTY: FeatureCollection<Point> = { type: "FeatureCollection", features: [] };

function csrfCookie(): string {
  const item = document.cookie.split("; ").find((part) => part.startsWith("mnm_csrf="));
  return item ? decodeURIComponent(item.slice("mnm_csrf=".length)) : "";
}

export default function InternalGeoMap() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [loginIdentifier, setLoginIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [organizationId, setOrganizationId] = useState("");
  const [loadedOrganization, setLoadedOrganization] = useState("");
  const [positionsCount, setPositionsCount] = useState(0);
  const [status, setStatus] = useState("Checking staff session…");
  const [working, setWorking] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: "/maps/maalenex-public-style.json",
      center: [38, 9],
      zoom: 5,
      minZoom: 3,
      maxZoom: 18,
      attributionControl: true,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl(), "top-right");
    map.addControl(new maplibregl.ScaleControl({ unit: "metric" }), "bottom-left");
    map.once("load", () => {
      map.addSource("internal-vehicle-positions", {
        type: "geojson",
        data: EMPTY,
      });
      map.addLayer({
        id: "internal-vehicle-position-points",
        type: "circle",
        source: "internal-vehicle-positions",
        paint: {
          "circle-radius": ["interpolate", ["linear"], ["zoom"], 5, 5, 14, 9],
          "circle-color": ["case", ["boolean", ["get", "is_synthetic"], false], "#d18a35", "#176b57"],
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2,
        },
      });
      map.addLayer({
        id: "internal-vehicle-position-labels",
        type: "symbol",
        source: "internal-vehicle-positions",
        layout: {
          "text-field": ["get", "vehicle_id"],
          "text-size": 10,
          "text-offset": [0, 1.3],
          "text-optional": true,
        },
        paint: { "text-color": "#173b34", "text-halo-color": "#ffffff", "text-halo-width": 1.2 },
      });
      setMapReady(true);
      setStatus("Map ready. Sign in and select an organization to load its vehicle positions.");
    });
    map.on("error", () => setStatus("Map renderer or public base geography is unavailable."));
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/v1/auth/sessions/current", {
      credentials: "include",
      signal: controller.signal,
    }).then((response) => {
      if (response.ok) {
        setAuthenticated(true);
        setStatus("Staff session verified. Enter an organization ID to load positions.");
      } else {
        setAuthenticated(false);
        setStatus("Staff sign-in is required.");
      }
    }).catch(() => {
      if (!controller.signal.aborted) setStatus("Unable to verify staff session.");
    });
    return () => controller.abort();
  }, []);

  async function signIn(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true);
    setStatus("Signing in…");
    try {
      const response = await fetch("/api/v1/auth/sessions", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login_identifier: loginIdentifier, password }),
      });
      if (!response.ok) throw new Error("signin");
      setPassword("");
      setAuthenticated(true);
      setStatus("Staff session verified. Enter an organization ID to load positions.");
    } catch {
      setAuthenticated(false);
      setStatus("Sign-in failed. Check the credentials and try again.");
    } finally {
      setWorking(false);
    }
  }

  useEffect(() => {
    if (!authenticated || !loadedOrganization || !mapReady) return;
    let cancelled = false;
    const refresh = async () => {
      const params = new URLSearchParams({
        organization_id: loadedOrganization,
        max_age_minutes: "30",
        limit: "500",
      });
      try {
        const response = await fetch(`/api/v1/geo/internal/vehicles/positions?${params.toString()}`, {
          credentials: "include",
          cache: "no-store",
        });
        if (response.status === 401) {
          setAuthenticated(false);
          setStatus("Staff session expired. Sign in again.");
          return;
        }
        if (response.status === 403) {
          setStatus("Access denied. Your account lacks tracking.read permission for this organization.");
          return;
        }
        if (!response.ok) throw new Error("positions");
        const payload = await response.json() as PositionsResponse;
        if (cancelled) return;
        const features: VehicleFeature[] = payload.positions.map((position) => ({
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [position.longitude, position.latitude],
          },
          properties: {
            vehicle_id: position.vehicle_id,
            speed_kph: position.speed_kph,
            heading_degrees: position.heading_degrees,
            accuracy_meters: position.accuracy_meters,
            recorded_at: position.recorded_at,
            is_synthetic: position.is_synthetic,
          },
        }));
        const source = mapRef.current?.getSource("internal-vehicle-positions") as maplibregl.GeoJSONSource | undefined;
        source?.setData({ type: "FeatureCollection", features });
        setPositionsCount(features.length);
        setStatus(`Showing ${features.length} recent vehicle position(s). Refreshes every 30 seconds.`);
      } catch {
        if (!cancelled) setStatus("Position service unavailable. No cached positions are displayed.");
      }
    };
    void refresh();
    const interval = window.setInterval(() => void refresh(), 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [authenticated, loadedOrganization, mapReady]);

  function loadTenant(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPositionsCount(0);
    const source = mapRef.current?.getSource("internal-vehicle-positions") as maplibregl.GeoJSONSource | undefined;
    source?.setData(EMPTY);
    setLoadedOrganization(organizationId.trim());
    setStatus("Authorizing organization scope and loading recent positions…");
  }

  async function signOut() {
    setWorking(true);
    try {
      await fetch("/api/v1/auth/sessions/current", {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRF-Token": csrfCookie() },
      });
    } finally {
      setAuthenticated(false);
      setLoadedOrganization("");
      setPositionsCount(0);
      const source = mapRef.current?.getSource("internal-vehicle-positions") as maplibregl.GeoJSONSource | undefined;
      source?.setData(EMPTY);
      setStatus("Signed out. Internal vehicle positions cleared.");
      setWorking(false);
    }
  }

  return (
    <main className="public-map-page">
      <header className="public-map-header">
        <a href="/" className="public-map-brand">MAALENEX</a>
        <a href="/map" className="public-map-home">Public geography map</a>
      </header>
      <section className="public-map-intro" aria-labelledby="internal-map-title">
        <p className="public-map-eyebrow">RESTRICTED OPERATIONS</p>
        <h1 id="internal-map-title">Internal vehicle map</h1>
        <p>Recent vehicle positions are available only to authenticated staff with permission for the selected organization. Data older than 30 minutes is excluded.</p>
        {!authenticated && <form className="internal-map-form" onSubmit={signIn}>
          <label>Staff login
            <input value={loginIdentifier} onChange={(event) => setLoginIdentifier(event.target.value)} autoComplete="username" required />
          </label>
          <label>Password
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
          </label>
          <button className="search-button" type="submit" disabled={working}>Sign in</button>
        </form>}
        {authenticated && <form className="internal-map-form" onSubmit={loadTenant}>
          <label>Organization ID
            <input value={organizationId} onChange={(event) => setOrganizationId(event.target.value)} placeholder="UUID of the authorized operator organization" required />
          </label>
          <button className="search-button" type="submit" disabled={working || !organizationId.trim()}>Load positions</button>
          <button className="secondary-button" type="button" onClick={signOut} disabled={working}>Sign out</button>
        </form>}
        <p className="public-map-status" role="status" aria-live="polite">{status}</p>
        <p className="public-map-status">Positions currently shown: {positionsCount}. Orange markers identify synthetic telemetry.</p>
      </section>
      <div ref={containerRef} className="public-map-canvas" role="region" aria-label="Tenant-scoped internal vehicle positions map" />
      <footer className="public-map-footer">
        Internal positions are fetched from the authenticated MaaleNex API, not from public Martin tiles.
        Device identifiers and raw telemetry credentials are never sent to this map.
      </footer>
    </main>
  );
}