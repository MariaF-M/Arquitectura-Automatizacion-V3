import { Suspense, useEffect, useState } from 'react';
import { REMOTOS } from './remotos';
import { LimiteErrores } from './LimiteErrores';

/** Mismo contrato que src/eventos.ts de los microfrontends: es la única comunicación entre ellos. */
interface DetalleEvento { contexto: string; evento: string; descripcion: string; momento: string }

const leerRuta = () => decodeURIComponent(location.hash.replace(/^#\/?/, ''));

export default function App() {
  const [actual, setActual] = useState(leerRuta());
  const [actividad, setActividad] = useState<DetalleEvento[]>([]);

  // Navegación por URL (#/mf_inventario): permite enlaces directos a cada microfrontend
  useEffect(() => {
    const alCambiar = () => setActual(leerRuta());
    window.addEventListener('hashchange', alCambiar);
    return () => window.removeEventListener('hashchange', alCambiar);
  }, []);

  // El shell no conoce los dominios: solo escucha los eventos que publican los microfrontends
  useEffect(() => {
    const alEvento = (e: Event) => setActividad((a) => [(e as CustomEvent<DetalleEvento>).detail, ...a].slice(0, 12));
    window.addEventListener('farmacia:evento', alEvento);
    return () => window.removeEventListener('farmacia:evento', alEvento);
  }, []);

  const remoto = REMOTOS.find((r) => r.id === actual);

  return (
    <div className="sh-app">
      <aside className="sh-menu">
        <a className="sh-marca" href="#/">
          <span className="sh-logo" aria-hidden>℞</span>
          <span><b>Farmacia</b><br /><small>Hospitalaria</small></span>
        </a>
        <nav>
          {REMOTOS.map((r) => (
            <a key={r.id} href={`#/${r.id}`} className={r.id === actual ? 'sh-activo' : ''}>
              <span>{r.nombre}</span>
              <small className={`sh-clasif sh-clasif-${r.clasificacion.toLowerCase()}`}>{r.clasificacion}</small>
            </a>
          ))}
        </nav>
        <section className="sh-actividad">
          <h3>Actividad</h3>
          {actividad.length === 0 && <p>Los eventos de dominio aparecerán aquí.</p>}
          <ul>
            {actividad.map((a, i) => (
              <li key={i}><b>{a.evento}</b><span>{a.contexto} · {a.descripcion}</span></li>
            ))}
          </ul>
        </section>
      </aside>

      <main className="sh-contenido">
        {remoto ? (
          <LimiteErrores key={remoto.id} nombre={remoto.nombre} puerto={remoto.puerto}>
            <Suspense fallback={<p className="sh-cargando">Cargando microfrontend «{remoto.nombre}»…</p>}>
              <remoto.Componente />
            </Suspense>
          </LimiteErrores>
        ) : <Inicio />}
      </main>
    </div>
  );
}

function Inicio() {
  return (
    <div className="sh-inicio">
      <p className="sh-sobretitulo">Gestión de medicamentos · Farmacia hospitalaria</p>
      <h1>Seleccione un contexto</h1>
      <p>
        Cada opción del menú es un <b>microfrontend independiente</b>, construido y desplegado por separado
        y cargado aquí en tiempo de ejecución con Module Federation. Cada uno corresponde a un contexto
        delimitado del modelo ArchiMate y habla solo con su propio servicio del backend.
      </p>
      <div className="sh-tarjetas">
        {REMOTOS.map((r) => (
          <a key={r.id} href={`#/${r.id}`} className="sh-tarjeta">
            <small className={`sh-clasif sh-clasif-${r.clasificacion.toLowerCase()}`}>{r.clasificacion}</small>
            <b>{r.nombre}</b>
            <span>{r.dominio} · puerto {r.puerto}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
