// Microfrontend «Abastecimiento» (D-04 SUPPORTING) — REMOTO de Module Federation.
// Expone ./App, que el shell carga en tiempo de ejecución desde 5104/remoteEntry.js.
// Generado desde el modelo ArchiMate. Guía oficial: https://module-federation.io (plugin @module-federation/vite).
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { federation } from '@module-federation/vite';

// URL pública desde donde el navegador descarga este microfrontend (cambia al desplegar).
const URL_PUBLICA = process.env.MF_URL ?? 'http://localhost:5104/';

export default defineConfig({
  base: URL_PUBLICA,
  server: { port: 5104, strictPort: true, origin: URL_PUBLICA.replace(/\/$/, ''), cors: true },
  preview: { port: 5104, strictPort: true, cors: true },
  build: { target: 'chrome89' },
  plugins: [
    federation({
      name: 'mf_abastecimiento',
      filename: 'remoteEntry.js',
      exposes: { './App': './src/App.tsx' },
      // React se comparte como singleton: una sola copia en el navegador aunque haya 7 aplicaciones.
      shared: { react: { singleton: true }, 'react-dom': { singleton: true } },
      dts: false,
    }),
    react(),
  ],
});
