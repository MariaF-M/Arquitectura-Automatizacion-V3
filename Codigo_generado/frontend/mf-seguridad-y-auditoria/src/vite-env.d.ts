/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** URL del gateway, p. ej. http://localhost:8080/api. Si no se define, se llama directo al puerto del servicio. */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
