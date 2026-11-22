import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "VITE_");
  const configuredApiBase = (env.VITE_API_BASE_URL ?? "").trim();
  let apiCspOrigin = "";

  if (configuredApiBase) {
    const apiUrl = new URL(configuredApiBase);
    const localHosts = new Set(["localhost", "127.0.0.1", "::1"]);
    const isLocalDevelopment =
      apiUrl.protocol === "http:" && localHosts.has(apiUrl.hostname);
    if (apiUrl.protocol !== "https:" && !isLocalDevelopment) {
      throw new Error("VITE_API_BASE_URL must use HTTPS (HTTP is permitted only for localhost development).");
    }
    if (apiUrl.username || apiUrl.password || apiUrl.pathname !== "/" || apiUrl.search || apiUrl.hash) {
      throw new Error("VITE_API_BASE_URL must be an origin only, without credentials, path, query or fragment.");
    }
    apiCspOrigin = apiUrl.origin;
  }

  return {
    // Android WebView serves the packaged SPA from /assets/www/; relative URLs
    // keep built JS/CSS and public assets inside that trusted packaged directory.
    base: "./",
    plugins: [
      react(),
      {
        name: "maalenex-api-csp-origin",
        transformIndexHtml(html: string) {
          return html.replace("__MAALENEX_API_CSP_ORIGIN__", apiCspOrigin);
        },
      },
    ],
    server: {
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: false,
        },
      },
    },
  };
});
