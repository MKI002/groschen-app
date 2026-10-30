import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The built files go into the Python package, which serves them.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../backend/groschen/static",
    emptyOutDir: true,
    assetsInlineLimit: 0,
    sourcemap: false,
  },
  server: {
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8420" },
  },
});
