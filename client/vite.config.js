import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Whenever React tries to fetch '/chat', Vite will route it to localhost:8000
      "/chat": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
