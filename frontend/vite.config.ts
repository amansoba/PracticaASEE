
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api/eventos": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/eventos/, ""),
      },
      "/api/catalogo": {
        target: "http://127.0.0.1:8003",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/catalogo/, ""),
      },
      "/api/tienda": {
        target: "http://127.0.0.1:8004",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/tienda/, ""),
      },    
      "/api/auth": {
        target: "http://127.0.0.1:8001",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/auth/, ""),
      },
      
      "/api/proveedores": {
        target: "http://127.0.0.1:8005",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/proveedores/, ""),
      },
    },
  },
});
