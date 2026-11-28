// Keep MapLibre outside Vite's module graph. MapLibre v6 detects its
// CDN-hosted worker from import.meta.url and creates a same-origin Blob worker.
try {
  const maplibregl = await import("https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs");
  // Explicit same-origin Blob worker wrapper. The imported worker remains a
  // real CDN module, so its sibling maplibre-gl-shared.mjs resolves on UNPKG.
  const workerBlob = new Blob(
    ['import "https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl-worker.mjs";'],
    { type: "text/javascript" }
  );
  const workerUrl = URL.createObjectURL(workerBlob);
  maplibregl.setWorkerUrl(workerUrl);
  window.__maalenexMapLibreWorkerUrl = workerUrl;
  window.__maalenexMapLibre = maplibregl;
} catch (error) {
  window.__maalenexMapLibreError = error instanceof Error ? error.message : String(error);
  console.error("MaaleNex MapLibre CDN module failed: " + window.__maalenexMapLibreError);
}
