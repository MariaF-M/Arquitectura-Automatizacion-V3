// Shell — HOST de Module Federation. Compone en tiempo de ejecución un microfrontend por contexto
// delimitado (V8) más el de integraciones (V9). Generado desde el modelo ArchiMate.
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { federation } from '@module-federation/vite';

// Dónde vive cada microfrontend. Se puede cambiar al desplegar sin tocar el código.
const remoto = (nombre: string, variable: string, porDefecto: string) => ({
  type: 'module' as const,
  name: nombre,
  entry: (process.env[variable] ?? porDefecto) + 'remoteEntry.js',
});

export default defineConfig({
  server: { port: 5100, strictPort: true },
  preview: { port: 5100, strictPort: true },
  build: { target: 'chrome89' },
  plugins: [
    federation({
      name: 'shell',
      remotes: {
        mf_inventario: remoto('mf_inventario', 'MF_INVENTARIO_URL', 'http://localhost:5101/'),  // Inventario
        mf_vencimientos: remoto('mf_vencimientos', 'MF_VENCIMIENTOS_URL', 'http://localhost:5102/'),  // Vencimientos
        mf_planificacion_de_demanda: remoto('mf_planificacion_de_demanda', 'MF_PLANIFICACION_DE_DEMANDA_URL', 'http://localhost:5103/'),  // Planificación de Demanda
        mf_abastecimiento: remoto('mf_abastecimiento', 'MF_ABASTECIMIENTO_URL', 'http://localhost:5104/'),  // Abastecimiento
        mf_seguridad_y_auditoria: remoto('mf_seguridad_y_auditoria', 'MF_SEGURIDAD_Y_AUDITORIA_URL', 'http://localhost:5105/'),  // Seguridad y Auditoría
        mf_integraciones: remoto('mf_integraciones', 'MF_INTEGRACIONES_URL', 'http://localhost:5106/'),  // Integraciones
      },
      shared: { react: { singleton: true }, 'react-dom': { singleton: true } },
      dts: false,
    }),
    react(),
  ],
});
