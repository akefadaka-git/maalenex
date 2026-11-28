// Keep MapLibre outside Vite's module graph. MapLibre v6 detects its
// CDN-hosted worker from import.meta.url; the explicit Blob wrapper keeps the
// Worker constructor same-origin while the worker imports its sibling module.
window.__maalenexMapLibrePromise = (async () => {
  const maplibregl = await import("https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs");
  const workerBlob = new Blob(
    ['import "https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl-worker.mjs";'],
    { type: "text/javascript" }
  );
  const workerUrl = URL.createObjectURL(workerBlob);
  maplibregl.setWorkerUrl(workerUrl);
  window.__maalenexMapLibreWorkerUrl = workerUrl;
  window.__maalenexMapLibre = maplibregl;
  return maplibregl;
})().catch((error) => {
  window.__maalenexMapLibreError = error instanceof Error ? error.message : String(error);
  console.error("MaaleNex MapLibre CDN module failed: " + window.__maalenexMapLibreError);
  throw error;
});
