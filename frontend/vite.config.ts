import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The built files go into the Python package, which serves them. "vite build --mode demo"
// builds the web demo for GitHub Pages instead, served from the repository's folder.
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === "demo" ? "/groschen-app/" : "/",
  build: {
    outDir: mode === "demo" ? "dist-demo" : "../backend/groschen/static",
    emptyOutDir: true,
    assetsInlineLimit: 0,
    sourcemap: false,
  },
  server: {
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8420" },
  },
}));
