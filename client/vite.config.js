import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Keep local development on the same API route used by the deployed app.
      "/chat": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
