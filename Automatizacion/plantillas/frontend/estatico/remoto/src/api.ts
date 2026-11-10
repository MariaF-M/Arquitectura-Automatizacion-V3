// Cliente HTTP hacia el backend del contexto. Cada microfrontend habla SOLO con su propio servicio
// (o con la ACL, en el caso de integraciones): así no se acopla a otros contextos.

export interface Respuesta<T = unknown> {
  ok: boolean;
  estado: number;
  datos: T;
  error?: string;
}

/** URL base de un servicio: vía gateway si VITE_API_URL está definido; si no, directo a su puerto. */
export function urlServicio(carpeta: string, puerto: number): string {
  const gateway = import.meta.env.VITE_API_URL;
  return gateway ? `${gateway.replace(/\/$/, '')}/${carpeta}` : `http://localhost:${puerto}`;
}

export async function llamar<T = unknown>(base: string, ruta: string, cuerpo?: object): Promise<Respuesta<T>> {
  try {
    const r = await fetch(base + ruta, cuerpo === undefined
      ? { method: 'GET' }
      : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) });
    const texto = await r.text();
    const datos = (texto ? JSON.parse(texto) : null) as T;
    const error = !r.ok && datos && typeof datos === 'object' && 'error' in datos ? String((datos as { error: unknown }).error) : undefined;
    return { ok: r.ok, estado: r.status, datos, error: error ?? (r.ok ? undefined : `Error ${r.status}`) };
  } catch (e) {
    return { ok: false, estado: 0, datos: null as T, error: `No se pudo conectar con ${base} (${(e as Error).message})` };
  }
}
