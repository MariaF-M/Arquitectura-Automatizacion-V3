import { useEffect, useState } from 'react';
import { llamar } from '../api';

interface EventoBackend { evento?: string; contrato?: string; agregado_id?: string; ocurrido_en?: string }

/** Eventos de dominio publicados por el backend de este contexto (GET /eventos). */
export function PanelEventos({ base, version }: { base: string; version: number }) {
  const [eventos, setEventos] = useState<EventoBackend[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void llamar<EventoBackend[]>(base, '/eventos').then((r) => {
      if (r.ok) { setEventos([...(r.datos ?? [])].reverse().slice(0, 8)); setError(null); }
      else setError(r.error ?? 'Error');
    });
  }, [base, version]);

  return (
    <section className="mf-tarjeta">
      <h2>Eventos de dominio <small>V6</small></h2>
      {error && <p className="mf-mensaje mf-error">{error}</p>}
      {eventos.length === 0 && !error && <p className="mf-nota">Aún no hay eventos en esta sesión del servicio.</p>}
      <ul className="mf-lista mf-eventos">
        {eventos.map((e, i) => (
          <li key={i}>
            <b>{e.evento ?? e.contrato ?? 'evento'}</b>
            {e.contrato && <em className="mf-chip">{e.contrato}</em>}
            <code>{(e.agregado_id ?? '').slice(0, 8)}</code>
            <time>{e.ocurrido_en ? new Date(e.ocurrido_en).toLocaleTimeString() : ''}</time>
          </li>
        ))}
      </ul>
    </section>
  );
}
