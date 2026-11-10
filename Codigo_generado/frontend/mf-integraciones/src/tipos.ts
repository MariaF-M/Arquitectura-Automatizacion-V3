// Tipos del descriptor src/contexto.json, que el generador produce desde el modelo ArchiMate.

export type TipoAtributo = 'texto' | 'entero' | 'decimal' | 'fecha' | 'booleano';

/** Atributo de un agregado (spec.yaml), con sus invariantes declarativas. */
export interface Atributo {
  nombre: string;
  etiqueta: string;
  tipo: TipoAtributo;
  obligatorio: boolean;
  noNegativo: boolean;
  opciones: string[] | null;
  cifrado: boolean;
  inicial: string | number | boolean | null;
}

/** Comando = Application Process de V6. */
export interface Comando {
  nombre: string;
  ruta: string;
  crea: boolean;
  evento: string | null;
  restar: string | null;
  estado: string | null;
  requiere: string[];
  desdeEstados: string[];
  /** Atributos fecha que deben ser posteriores a hoy (validado también en el backend). */
  fechaFutura: string[];
}

/** Agregado = Data Object raíz de V6. */
export interface Agregado {
  nombre: string;
  recurso: string;
  atributos: Atributo[];
  invariantes: string[];
  comandos: Comando[];
}

export interface DescriptorContexto {
  tipo: 'contexto';
  nombre: string;
  carpeta: string;
  puerto: number;
  dominio: string;
  tituloDominio: string;
  clasificacion: string;
  lenguaje: string;
  arquitectura: string;
  baseDatos: string;
  agregados: Agregado[];
  funciones: { nombre: string; ruta: string }[];
  componentes: string[];
  entidades: string[];
  relaciones: { con: string; patron: string; sentido: 'consume' | 'provee' }[];
}

/** Integración INT-xx de V9. */
export interface Integracion {
  codigo: string;
  ruta: string;
  nombre: string;
  externo: string;
  objeto: string;
  direccion: 'entrada' | 'salida';
  contexto: string;
  carpetaContexto: string;
  puertoContexto: number;
  recursoContexto: string | null;
  comando: string | null;
  evento: string | null;
  campos: string[];
  campoId: string | null;
  mapeo: Record<string, string>;
}

export interface DescriptorIntegraciones {
  tipo: 'integraciones';
  nombre: string;
  carpeta: string;
  puerto: number;
  interfaz: string;
  integraciones: Integracion[];
}

export type Descriptor = DescriptorContexto | DescriptorIntegraciones;

export type Fila = Record<string, unknown> & { id: string };
