import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // Android WebView serves the packaged SPA from /assets/www/; relative URLs
  // keep built JS/CSS and public assets inside that trusted packaged directory.
  base: "./",
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: false,
      },
    },
  },
});
