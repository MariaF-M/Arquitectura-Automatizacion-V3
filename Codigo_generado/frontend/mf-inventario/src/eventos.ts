// Comunicación entre microfrontends con CustomEvents del navegador (recomendación de
// martinfowler.com/articles/micro-frontends.html): mínima, sin estado compartido.
// El shell escucha 'farmacia:evento' para mostrar la actividad de todos los contextos.

export const NOMBRE_EVENTO = 'farmacia:evento';

export interface DetalleEvento {
  contexto: string;
  evento: string;
  descripcion: string;
  momento: string;
}

export function emitir(contexto: string, evento: string, descripcion: string): void {
  const detail: DetalleEvento = { contexto, evento, descripcion, momento: new Date().toISOString() };
  window.dispatchEvent(new CustomEvent<DetalleEvento>(NOMBRE_EVENTO, { detail }));
}
