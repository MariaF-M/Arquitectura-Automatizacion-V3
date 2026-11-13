import { useCallback, useEffect, useState, type FormEvent } from 'react';
import type { Agregado, Atributo, Comando, Fila } from '../tipos';
import { llamar } from '../api';
import { emitir } from '../eventos';
import { Campo, convertir, validar } from './Campo';

interface Props { agregado: Agregado; base: string; contexto: string; alCambiar: () => void }

/** Un agregado de V6: tabla de instancias, formulario del comando que lo crea y acciones del resto de comandos. */
export function PanelAgregado({ agregado, base, contexto, alCambiar }: Props) {
  const [filas, setFilas] = useState<Fila[]>([]);
  const [mensaje, setMensaje] = useState<{ tipo: 'ok' | 'error'; texto: string } | null>(null);
  const [abierto, setAbierto] = useState<{ fila: Fila; comando: Comando } | null>(null);

  const recurso = `/${agregado.recurso}`;
  const creador = agregado.comandos.find((c) => c.crea);
  const acciones = agregado.comandos.filter((c) => !c.crea);
  // En la creación no se piden los campos que el dominio inicializa (p. ej. estado = Disponible)
  const camposCrear = agregado.atributos.filter((a) => a.inicial === null || a.inicial === undefined);

  const cargar = useCallback(async () => {
    const r = await llamar<Fila[]>(base, recurso);
    if (r.ok) setFilas(r.datos ?? []);
    else setMensaje({ tipo: 'error', texto: r.error ?? 'Error' });
  }, [base, recurso]);

  useEffect(() => { void cargar(); }, [cargar]);

  async function ejecutar(comando: Comando, ruta: string, cuerpo: object) {
    const r = await llamar<Fila>(base, ruta, cuerpo);
    if (r.ok) {
      setMensaje({ tipo: 'ok', texto: comando.evento ? `«${comando.nombre}» ejecutado → evento «${comando.evento}»` : `«${comando.nombre}» ejecutado` });
      if (comando.evento) emitir(contexto, comando.evento, `${agregado.nombre} ${r.datos?.id?.slice(0, 8) ?? ''}`);
      setAbierto(null);
      await cargar();
      alCambiar();
      return true;
    }
    setMensaje({ tipo: 'error', texto: r.error ?? 'Error' });
    return false;
  }

  async function deshacer(fila: Fila) {
    const r = await llamar(base, `${recurso}/${fila.id}/deshacer`, {});
    setMensaje(r.ok ? { tipo: 'ok', texto: 'Último cambio deshecho (memento)' } : { tipo: 'error', texto: r.error ?? 'Error' });
    await cargar();
  }

  const permitido = (c: Comando, f: Fila) => c.desdeEstados.length === 0 || c.desdeEstados.includes(String(f.estado));

  return (
    <section className="mf-tarjeta">
      <div className="mf-tarjeta-titulo">
        <h2>{agregado.nombre} <small>agregado raíz</small></h2>
        <button className="mf-boton mf-secundario" onClick={() => void cargar()}>Actualizar</button>
      </div>

      {agregado.invariantes.length > 0 && (
        <details className="mf-invariantes">
          <summary>Invariantes que protege ({agregado.invariantes.length})</summary>
          <ul>{agregado.invariantes.map((i) => <li key={i}>{i}</li>)}</ul>
        </details>
      )}

      {mensaje && <p className={`mf-mensaje mf-${mensaje.tipo}`} role="status">{mensaje.texto}</p>}

      {creador && (
        <FormularioComando titulo={creador.nombre} evento={creador.evento} campos={camposCrear} fechaFutura={creador.fechaFutura}
          alEnviar={(datos) => ejecutar(creador, `${recurso}/${creador.ruta}`, datos)} />
      )}

      <div className="mf-tabla-contenedor">
        <table className="mf-tabla">
          <thead>
            <tr>
              <th>id</th>
              {agregado.atributos.map((a) => <th key={a.nombre}>{a.etiqueta}</th>)}
              <th>Comandos</th>
            </tr>
          </thead>
          <tbody>
            {filas.length === 0 && (
              <tr><td colSpan={agregado.atributos.length + 2} className="mf-vacio">Sin registros todavía</td></tr>
            )}
            {filas.map((f) => (
              <tr key={f.id}>
                <td title={f.id}><code>{f.id.slice(0, 8)}</code></td>
                {agregado.atributos.map((a) => <td key={a.nombre}>{formatear(f[a.nombre])}</td>)}
                <td className="mf-acciones">
                  {acciones.map((c) => (
                    <button key={c.ruta} className="mf-boton" disabled={!permitido(c, f)}
                      title={permitido(c, f) ? c.nombre : `Solo desde: ${c.desdeEstados.join(', ')}`}
                      onClick={() => setAbierto({ fila: f, comando: c })}>{c.nombre}</button>
                  ))}
                  <button className="mf-boton mf-secundario" onClick={() => void deshacer(f)} title="Restaura el estado anterior (patrón Memento)">Deshacer</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {abierto && (
        <div className="mf-modal" role="dialog" aria-label={abierto.comando.nombre}>
          <FormularioComando
            titulo={`${abierto.comando.nombre} · ${abierto.fila.id.slice(0, 8)}`}
            evento={abierto.comando.evento}
            fechaFutura={abierto.comando.fechaFutura}
            {...camposDeAccion(agregado.atributos, abierto.comando)}
            alCancelar={() => setAbierto(null)}
            alEnviar={(datos) => ejecutar(abierto.comando, `${recurso}/${abierto.fila.id}/${abierto.comando.ruta}`, datos)} />
        </div>
      )}
    </section>
  );
}

/** Qué campos pide cada comando: el que se resta, los requeridos y, opcionalmente, el resto. */
function camposDeAccion(atributos: Atributo[], c: Comando): { campos: Atributo[]; opcionales?: Atributo[] } {
  const por = (n: string) => atributos.find((a) => a.nombre === n);
  // la cantidad a restar debe ser positiva (el backend también lo exige)
  if (c.restar) return { campos: [{ ...por(c.restar)!, obligatorio: true, minimo: 1 }] };
  const requeridos = c.requiere.map(por).filter((a): a is Atributo => !!a).map((a) => ({ ...a, obligatorio: true }));
  const opcionales = atributos
    .filter((a) => !c.requiere.includes(a.nombre) && !(c.estado && a.nombre === 'estado'))
    .map((a) => ({ ...a, obligatorio: false }));
  return { campos: requeridos, opcionales };
}

/** Mañana en formato yyyy-mm-dd (fecha local), mínimo para las fechas que deben ser futuras. */
function manana(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function FormularioComando({ titulo, evento, campos, opcionales = [], fechaFutura = [], alEnviar, alCancelar }: {
  titulo: string; evento: string | null; campos: Atributo[]; opcionales?: Atributo[]; fechaFutura?: string[];
  alEnviar: (datos: Record<string, unknown>) => Promise<boolean>; alCancelar?: () => void;
}) {
  const [valores, setValores] = useState<Record<string, string>>({});
  const [enviando, setEnviando] = useState(false);
  const [errores, setErrores] = useState<string[]>([]);
  const cambiar = (n: string) => (v: string) => setValores((x) => ({ ...x, [n]: v }));

  async function enviar(e: FormEvent) {
    e.preventDefault();
    const minimas = Object.fromEntries(fechaFutura.map((f) => [f, manana()]));
    const encontrados = validar([...campos, ...opcionales], valores, minimas);
    setErrores(encontrados);
    if (encontrados.length > 0) return;          // no se envía nada al backend si hay errores
    setEnviando(true);
    const ok = await alEnviar(convertir([...campos, ...opcionales], valores));
    setEnviando(false);
    if (ok) setValores({});
  }

  return (
    <form className="mf-formulario" noValidate onSubmit={(e) => void enviar(e)}>
      <h3>{titulo}{evento && <small> → emite «{evento}»</small>}</h3>
      <div className="mf-rejilla">
        {campos.map((a) => <Campo key={a.nombre} a={a} valor={valores[a.nombre] ?? ''} cambiar={cambiar(a.nombre)}
          minimo={fechaFutura.includes(a.nombre) ? manana() : undefined} />)}
        {campos.length === 0 && opcionales.length === 0 && <p className="mf-nota">Este comando no necesita datos.</p>}
      </div>
      {opcionales.length > 0 && (
        <details className="mf-opcionales">
          <summary>Otros campos (opcional)</summary>
          <div className="mf-rejilla">
            {opcionales.map((a) => <Campo key={a.nombre} a={a} valor={valores[a.nombre] ?? ''} cambiar={cambiar(a.nombre)}
          minimo={fechaFutura.includes(a.nombre) ? manana() : undefined} />)}
          </div>
        </details>
      )}
      {errores.length > 0 && (
        <ul className="mf-mensaje mf-error mf-errores" role="alert">
          {errores.map((x) => <li key={x}>{x}</li>)}
        </ul>
      )}
      <div className="mf-botonera">
        {alCancelar && <button type="button" className="mf-boton mf-secundario" onClick={alCancelar}>Cancelar</button>}
        <button type="submit" className="mf-boton mf-primario" disabled={enviando}>{enviando ? 'Enviando…' : 'Ejecutar'}</button>
      </div>
    </form>
  );
}

function formatear(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—';
  return String(v);
}
