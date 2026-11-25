import { useEffect, useRef, useState } from "react";
import maplibregl, { type Map as MapLibreMap } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import "./public-map.css";

const STYLE_URL = "/maps/maalenex-public-style.json";

export default function PublicGeoMap() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const [status, setStatus] = useState("Loading approved public geography…");

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: STYLE_URL,
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
      setStatus("Map renderer ready. Only approved, published geography is requested.");
    });
    map.on("error", () => {
      setStatus("Public map data is unavailable. Check the Martin service and published geo_public views.");
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return (
    <main className="public-map-page">
      <header className="public-map-header">
        <a href="/" className="public-map-brand">MAALENEX</a>
        <a href="/" className="public-map-home">Return to passenger platform</a>
      </header>
      <section className="public-map-intro" aria-labelledby="public-map-title">
        <p className="public-map-eyebrow">PUBLIC GEOGRAPHY</p>
        <h1 id="public-map-title">MaaleNex Map</h1>
        <p>Published locations, terminals, routes, boundaries and roads. Unverified and unpublished records are not displayed.</p>
        <p className="public-map-status" role="status" aria-live="polite">{status}</p>
      </section>
      <div
        ref={containerRef}
        className="public-map-canvas"
        role="region"
        aria-label="Map of approved and published MaaleNex geographic features"
      />
      <footer className="public-map-footer">
        Map tiles are generated from the canonical MaaleNex PostGIS database by Martin.
        Internal vehicle positions, device identifiers and staff-only operational data are not part of this public map.
      </footer>
    </main>
  );
}