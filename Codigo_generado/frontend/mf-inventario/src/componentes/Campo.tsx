import { useId } from 'react';
import type { Atributo } from '../tipos';

/** Un campo de formulario según el tipo del atributo (texto, entero, decimal, fecha, booleano, lista). */
export function Campo({ a, valor, cambiar, requerido, minimo }: {
  a: Atributo; valor: string; cambiar: (v: string) => void; requerido?: boolean; minimo?: string;
}) {
  const obligatorio = requerido ?? a.obligatorio;
  const id = useId();
  let control;
  if (a.opciones) {
    control = (
      <select id={id} value={valor} onChange={(e) => cambiar(e.target.value)} required={obligatorio}>
        <option value="">— seleccione —</option>
        {a.opciones.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    );
  } else if (a.tipo === 'booleano') {
    control = <input id={id} type="checkbox" checked={valor === 'true'} onChange={(e) => cambiar(String(e.target.checked))} />;
  } else {
    const tipo = a.tipo === 'fecha' ? 'date' : a.tipo === 'texto' ? 'text' : 'number';
    control = (
      <input id={id} type={tipo} value={valor} required={obligatorio}
        step={a.tipo === 'decimal' ? 'any' : undefined}
        min={minimo ?? (a.noNegativo && a.tipo !== 'fecha' ? 0 : undefined)}
        onChange={(e) => cambiar(e.target.value)} />
    );
  }
  return (
    <label className="mf-campo" htmlFor={id}>
      <span>
        {a.etiqueta}{obligatorio && <b className="mf-req"> *</b>}
        {a.cifrado && <em className="mf-chip mf-chip-cifrado" title="Se guarda cifrado en la base de datos">cifrado</em>}
      </span>
      {control}
    </label>
  );
}

/** Convierte los valores del formulario al tipo de cada atributo; omite los vacíos. */
export function convertir(atributos: Atributo[], valores: Record<string, string>): Record<string, unknown> {
  const salida: Record<string, unknown> = {};
  for (const a of atributos) {
    const v = valores[a.nombre];
    if (v === undefined || v === '') continue;
    salida[a.nombre] = a.tipo === 'entero' ? parseInt(v, 10)
      : a.tipo === 'decimal' ? parseFloat(v)
      : a.tipo === 'booleano' ? v === 'true'
      : v;
  }
  return salida;
}
