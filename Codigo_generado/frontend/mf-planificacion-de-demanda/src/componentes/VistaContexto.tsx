import type { DescriptorContexto } from '../tipos';
import { urlServicio } from '../api';
import { PanelAgregado } from './PanelAgregado';

/** Vista de un contexto delimitado: encabezado (V5/V8) y un panel por agregado (V6). */
export function VistaContexto({ d }: { d: DescriptorContexto }) {
  const base = urlServicio(d.carpeta, d.puerto);

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
          <p className="mf-nota">Este dominio es genérico y no tiene agregados en V6. Expone sus servicios a los demás contextos (Open Host Service).</p>
          <ul className="mf-lista">{d.componentes.map((c) => <li key={c}>{c}</li>)}</ul>
          <p className="mf-nota">Entidades: {d.entidades.join(', ')}</p>
        </section>
      )}

      {d.agregados.map((a) => (
        <PanelAgregado key={a.recurso} agregado={a} base={base} contexto={d.nombre} />
      ))}
    </>
  );
}
