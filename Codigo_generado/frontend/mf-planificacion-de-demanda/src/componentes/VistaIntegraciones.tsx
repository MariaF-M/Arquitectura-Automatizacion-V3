import { useEffect, useState, type FormEvent } from 'react';
import type { DescriptorIntegraciones, Fila, Integracion } from '../tipos';
import { llamar, urlServicio } from '../api';
import { emitir } from '../eventos';

/**
 * Simulador de sistemas externos (V9). Cada tarjeta es una integración INT-xx: se escribe el mensaje
 * EN EL FORMATO DEL EXTERNO y la ACL-01 lo traduce al lenguaje ubicuo del contexto interno (o al revés).
 */
export function VistaIntegraciones({ d }: { d: DescriptorIntegraciones }) {
  const base = urlServicio(d.carpeta, d.puerto);
  return (
    <>
      <header className="mf-encabezado">
        <div>
          <p className="mf-sobretitulo">V9 · Interoperabilidad y anticorrupción · {d.interfaz}</p>
          <h1>{d.nombre}</h1>
        </div>
        <div className="mf-chips"><span className="mf-chip mf-clasif-acl">ACL</span><span className="mf-chip">Java</span><span className="mf-chip">hexagonal</span></div>
      </header>
      <p className="mf-nota mf-intro">
        Aquí se simulan los sistemas externos. Ningún contexto interno conoce estos formatos: la capa
        anticorrupción traduce cada mensaje y lo entrega como comando (entrada) o lo envía al externo (salida).
      </p>
      <div className="mf-rejilla-tarjetas">
        {d.integraciones.map((i) => <TarjetaIntegracion key={i.codigo} i={i} base={base} />)}
      </div>
    </>
  );
}

function TarjetaIntegracion({ i, base }: { i: Integracion; base: string }) {
  const [valores, setValores] = useState<Record<string, string>>({});
  const [opcionesId, setOpcionesId] = useState<Fila[]>([]);
  const [resultado, setResultado] = useState<{ ok: boolean; texto: string } | null>(null);
  const entrada = i.direccion === 'entrada';

  // Si el comando actúa sobre un agregado existente, se ofrece la lista de ese contexto
  useEffect(() => {
    if (!i.campoId || !i.recursoContexto) return;
    void llamar<Fila[]>(urlServicio(i.carpetaContexto, i.puertoContexto), `/${i.recursoContexto}`)
      .then((r) => setOpcionesId(r.ok ? r.datos ?? [] : []));
  }, [i, resultado]);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    const mensaje: Record<string, unknown> = {};
    for (const c of i.campos) {
      const v = valores[c] ?? '';
      if (v !== '') mensaje[c] = /^-?\d+(\.\d+)?$/.test(v) && c !== i.campoId ? Number(v) : v;
    }
    const r = await llamar(base, `/${entrada ? 'entrantes' : 'salientes'}/${i.ruta}`, mensaje);
    setResultado({ ok: r.ok, texto: r.ok ? JSON.stringify(r.datos, null, 2) : (r.error ?? 'Error') });
    if (r.ok) emitir('ACL-01', i.codigo, entrada ? `${i.externo} → ${i.contexto}` : `${i.contexto} → ${i.externo}`);
  }

  return (
    <section className="mf-tarjeta">
      <div className="mf-tarjeta-titulo">
        <h2>{i.codigo} <small>{i.nombre}</small></h2>
        <span className={`mf-chip mf-dir-${i.direccion}`}>{entrada ? 'entrada' : 'salida'}</span>
      </div>
      <p className="mf-flujo">
        {entrada
          ? <><b>{i.externo}</b> → ACL-01 → <b>{i.contexto}</b> · comando «{i.comando}»</>
          : <><b>{i.contexto}</b> (evento «{i.evento}») → ACL-01 → <b>{i.externo}</b></>}
      </p>
      <p className="mf-nota">Objeto intercambiado: {i.objeto}</p>
      <form className="mf-formulario" onSubmit={(e) => void enviar(e)}>
        <div className="mf-rejilla">
          {i.campos.map((c) => (
            <label key={c} className="mf-campo">
              <span>{c} <em className="mf-nota">→ {i.mapeo[c]}</em></span>
              {c === i.campoId ? (
                <select value={valores[c] ?? ''} onChange={(e) => setValores((x) => ({ ...x, [c]: e.target.value }))} required>
                  <option value="">— elegir en {i.contexto} —</option>
                  {opcionesId.map((f) => (
                    <option key={f.id} value={f.id}>{f.id.slice(0, 8)} · {String(f.codigo ?? f.lote_codigo ?? f.estado ?? '')}</option>
                  ))}
                </select>
              ) : (
                <input value={valores[c] ?? ''} onChange={(e) => setValores((x) => ({ ...x, [c]: e.target.value }))} />
              )}
            </label>
          ))}
        </div>
        <div className="mf-botonera"><button className="mf-boton mf-primario" type="submit">Enviar a la ACL</button></div>
      </form>
      {resultado && <pre className={`mf-resultado mf-${resultado.ok ? 'ok' : 'error'}`}>{resultado.texto}</pre>}
    </section>
  );
}
