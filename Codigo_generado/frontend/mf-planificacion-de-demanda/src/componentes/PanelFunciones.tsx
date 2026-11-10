import { useState } from 'react';
import { llamar } from '../api';

/** Application Functions de V5. Su lógica no está en el diagrama: el backend responde 501 hasta implementarlas. */
export function PanelFunciones({ funciones, base }: { funciones: { nombre: string; ruta: string }[]; base: string }) {
  const [respuesta, setRespuesta] = useState<Record<string, string>>({});

  async function ejecutar(ruta: string) {
    const r = await llamar(base, `/funciones/${ruta}`, {});
    setRespuesta((x) => ({ ...x, [ruta]: r.estado === 501 ? 'Pendiente de implementar (501)' : r.ok ? 'OK' : (r.error ?? 'Error') }));
  }

  return (
    <section className="mf-tarjeta">
      <h2>Funciones <small>V5</small></h2>
      <ul className="mf-lista">
        {funciones.map((f) => (
          <li key={f.ruta}>
            <span>{f.nombre}</span>
            <button className="mf-boton mf-secundario" onClick={() => void ejecutar(f.ruta)}>Probar</button>
            {respuesta[f.ruta] && <em className="mf-nota">{respuesta[f.ruta]}</em>}
          </li>
        ))}
      </ul>
    </section>
  );
}
