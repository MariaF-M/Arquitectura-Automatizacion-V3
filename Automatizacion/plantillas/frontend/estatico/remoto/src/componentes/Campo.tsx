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
        min={minimo ?? (a.tipo !== 'fecha' && a.minimo !== null ? a.minimo : undefined)}
        max={a.tipo !== 'fecha' && a.maximo !== null ? a.maximo : undefined}
        maxLength={a.tipo === 'texto' && a.maxLargo ? a.maxLargo : undefined}
        title={a.mensaje ?? undefined}
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

/**
 * Control de errores en el navegador, con las mismas reglas del backend (spec.yaml).
 * Devuelve la lista de errores en español; vacía si todo está bien.
 */
export function validar(atributos: Atributo[], valores: Record<string, string>, fechaMinima?: Record<string, string>): string[] {
  const errores: string[] = [];
  for (const a of atributos) {
    const v = (valores[a.nombre] ?? '').trim();
    if (v === '') {
      if (a.obligatorio) errores.push(`«${a.etiqueta}» es obligatorio.`);
      continue;
    }
    if (a.tipo === 'entero' && !/^-?\d+$/.test(v)) { errores.push(`«${a.etiqueta}» debe ser un número entero.`); continue; }
    if (a.tipo === 'decimal' && Number.isNaN(Number(v.replace(',', '.')))) { errores.push(`«${a.etiqueta}» debe ser un número.`); continue; }
    if (a.tipo === 'fecha' && !/^\d{4}-\d{2}-\d{2}$/.test(v)) { errores.push(`«${a.etiqueta}» debe ser una fecha válida.`); continue; }
    if (a.tipo === 'entero' || a.tipo === 'decimal') {
      const n = Number(v.replace(',', '.'));
      if (a.minimo !== null && n < a.minimo) errores.push(`«${a.etiqueta}» debe ser mayor o igual a ${a.minimo}.`);
      if (a.maximo !== null && n > a.maximo) errores.push(`«${a.etiqueta}» debe ser menor o igual a ${a.maximo}.`);
    }
    if (a.tipo === 'texto') {
      if (a.maxLargo && v.length > a.maxLargo) errores.push(`«${a.etiqueta}» admite máximo ${a.maxLargo} caracteres.`);
      if (a.patron && !new RegExp(a.patron).test(v)) errores.push(`«${a.etiqueta}» ${a.mensaje ?? 'no tiene el formato esperado'}.`);
    }
    const minFecha = fechaMinima?.[a.nombre];
    if (a.tipo === 'fecha' && minFecha && v < minFecha) errores.push(`«${a.etiqueta}» debe ser posterior a hoy.`);
  }
  return errores;
}

/** Convierte los valores del formulario al tipo de cada atributo; omite los vacíos. */
export function convertir(atributos: Atributo[], valores: Record<string, string>): Record<string, unknown> {
  const salida: Record<string, unknown> = {};
  for (const a of atributos) {
    const v = (valores[a.nombre] ?? '').trim();
    if (v === '') continue;
    salida[a.nombre] = a.tipo === 'entero' ? parseInt(v, 10)
      : a.tipo === 'decimal' ? parseFloat(v.replace(',', '.'))
      : a.tipo === 'booleano' ? v === 'true'
      : v;
  }
  return salida;
}
