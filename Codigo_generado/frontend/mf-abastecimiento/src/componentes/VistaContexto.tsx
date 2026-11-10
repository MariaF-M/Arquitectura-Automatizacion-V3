import { useState } from 'react';
import type { DescriptorContexto } from '../tipos';
import { urlServicio } from '../api';
import { PanelAgregado } from './PanelAgregado';
import { PanelEventos } from './PanelEventos';
import { PanelFunciones } from './PanelFunciones';

/** Vista de un contexto delimitado: encabezado (V5/V8), un panel por agregado (V6), funciones (V5) y eventos. */
export function VistaContexto({ d }: { d: DescriptorContexto }) {
  const base = urlServicio(d.carpeta, d.puerto);
  const [version, setVersion] = useState(0);   // sube después de cada comando para refrescar los eventos
  const refrescar = () => setVersion((v) => v + 1);

  return (
    <>
      <header className="mf-encabezado">
        <div>
          <p className="mf-sobretitulo">{d.dominio} · {d.tituloDominio}</p>
          <h1>{d.nombre}</h1>
        </div>
        <div className="mf-chips">
          <span className={`mf-chip mf-clasif-${d.clasificacion.toLowerCase()}`}>{d.clasificacion}</span>
          <span className="mf-chip">{d.lenguaje}</span>
          <span className="mf-chip">{d.arquitectura}</span>
          <span className="mf-chip">{d.baseDatos}</span>
        </div>
      </header>

      {d.relaciones.length > 0 && (
        <p className="mf-relaciones">
          {d.relaciones.map((r) => (
            <span key={r.con + r.patron} className="mf-relacion">
              {r.sentido === 'consume' ? 'consume a' : 'le sirve a'} <b>{r.con}</b> <em>«{r.patron}»</em>
            </span>
          ))}
        </p>
      )}

      {d.agregados.length === 0 && (
        <section className="mf-tarjeta">
          <h2>Componentes del dominio</h2>
          <p className="mf-nota">Este dominio no tiene agregados en V6; expone componentes y funciones.</p>
          <ul className="mf-lista">{d.componentes.map((c) => <li key={c}>{c}</li>)}</ul>
          <p className="mf-nota">Entidades: {d.entidades.join(', ')}</p>
        </section>
      )}

      {d.agregados.map((a) => (
        <PanelAgregado key={a.recurso} agregado={a} base={base} contexto={d.nombre} alCambiar={refrescar} />
      ))}

      <div className="mf-columnas">
        <PanelFunciones funciones={d.funciones} base={base} />
        <PanelEventos base={base} version={version} />
      </div>
    </>
  );
}
