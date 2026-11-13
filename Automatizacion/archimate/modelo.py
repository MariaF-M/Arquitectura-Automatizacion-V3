"""Modelo intermedio: lo que el generador entiende, independiente de ArchiMate y del lenguaje destino.

Cada objeto guarda `origen`, el id del elemento del diagrama del que salió, para la trazabilidad.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from . import nombres as n

TIPOS_VALIDOS = {"texto", "entero", "decimal", "fecha", "booleano"}


@dataclass
class Atributo:
    nombre: str
    tipo: str
    # Reglas de formato (spec.yaml -> formatos). Se validan en backend y frontend.
    patron: str | None = None       # expresión regular que debe cumplir el texto completo
    mensaje: str | None = None      # explicación legible del patrón
    minimo: float | None = None
    maximo: float | None = None
    max_largo: int | None = None    # largo máximo de un texto

    @property
    def snake(self): return n.snake(self.nombre)
    @property
    def camel(self): return n.camel(self.nombre)
    @property
    def pascal(self): return n.pascal(self.nombre)


@dataclass
class Evento:
    nombre: str
    origen: str
    @property
    def clase(self): return n.pascal(self.nombre)


@dataclass
class Comando:
    nombre: str
    origen: str
    evento: Evento | None
    crea: bool = False
    restar: str | None = None
    nuevo_estado: str | None = None
    requiere: list[str] = field(default_factory=list)
    desde_estados: list[str] = field(default_factory=list)
    fecha_futura: list[str] = field(default_factory=list)   # fechas que deben ser posteriores a hoy

    @property
    def clase(self): return n.pascal(self.nombre)
    @property
    def metodo_snake(self): return n.snake(self.nombre)
    @property
    def metodo_camel(self): return n.camel(self.nombre)
    @property
    def ruta(self): return n.kebab(self.nombre)


@dataclass
class Agregado:
    nombre: str
    origen: str
    atributos: list[Atributo]
    comandos: list[Comando]
    eventos: list[Evento]
    valores_iniciales: dict = field(default_factory=dict)
    obligatorios: list[str] = field(default_factory=list)
    no_negativos: list[str] = field(default_factory=list)
    valores_permitidos: dict = field(default_factory=dict)
    invariantes: list[str] = field(default_factory=list)
    unicos: list[str] = field(default_factory=list)      # atributos que no se pueden repetir entre agregados

    @property
    def clase(self): return n.pascal(self.nombre)
    @property
    def snake(self): return n.snake(self.nombre)
    @property
    def recurso(self): return n.kebab(self.nombre)


@dataclass
class Entidad:
    nombre: str
    origen: str
    atributos: list[Atributo]
    compartida: bool = False     # True si es el núcleo compartido (Shared Kernel)

    @property
    def clase(self): return n.pascal(self.nombre)
    @property
    def snake(self): return n.snake(self.nombre)


@dataclass
class Funcion:
    """Application Function de V5: un caso de uso del contexto."""
    nombre: str
    origen: str
    @property
    def clase(self): return n.pascal(self.nombre)
    @property
    def snake(self): return n.snake(self.nombre)
    @property
    def ruta(self): return n.kebab(self.nombre)


@dataclass
class Componente:
    """Application Component de V5: un servicio de aplicación dentro del contexto."""
    nombre: str
    origen: str
    @property
    def clase(self): return n.pascal(self.nombre)
    @property
    def snake(self): return n.snake(self.nombre)


@dataclass
class RelacionContexto:
    """Relación de V8 entre contextos internos (o con la ACL)."""
    patron: str            # customer-supplier | shared-kernel | open-host-service | acl
    etiqueta: str          # texto escrito en la relación del diagrama
    proveedor: str         # nombre del contexto que sirve / provee
    cliente: str           # nombre del contexto que consume
    origen: str
    detalle: str = ""      # p. ej. el concepto compartido en Shared Kernel


@dataclass
class Integracion:
    codigo: str            # INT-01
    nombre: str            # Programación quirúrgica
    origen: str
    objeto: str            # OBJ-01 — Agenda quirúrgica confirmada
    objeto_origen: str
    externo: str           # sistema externo en V8
    contexto: str          # contexto interno afectado (deducido de V8)
    direccion: str         # entrada | salida
    comando: str | None
    evento: str | None
    mapeo: dict
    externo_origen: str = ""   # id del componente externo en V8
    relacion_v8: str = ""      # id de la relación «ACL» en V8

    @property
    def ruta(self): return n.kebab(self.codigo)
    @property
    def clase(self): return n.pascal(self.codigo + " " + self.nombre)
    @property
    def dto(self): return n.pascal(self.objeto.split("—")[-1])


@dataclass
class Contexto:
    nombre: str
    origen: str
    dominio: str
    titulo_dominio: str
    clasificacion: str      # CORE | SUPPORTING | GENERIC
    lenguaje: str
    arquitectura: str       # hexagonal | microservicios
    puerto: int
    base_datos: dict
    cache: dict
    cifrado: list[str]
    componentes: list[Componente] = field(default_factory=list)
    funciones: list[Funcion] = field(default_factory=list)
    entidades: list[Entidad] = field(default_factory=list)
    agregados: list[Agregado] = field(default_factory=list)
    proveedores: list[RelacionContexto] = field(default_factory=list)   # contextos de los que consume
    consumidores: list[RelacionContexto] = field(default_factory=list)  # contextos que lo consumen
    integraciones: list[Integracion] = field(default_factory=list)
    grupo_v6: str = ""      # id del Grouping de V6 del dominio

    @property
    def clase(self): return n.pascal(self.nombre)
    @property
    def snake(self): return n.snake(self.nombre)
    @property
    def carpeta(self): return n.kebab(self.nombre)
    @property
    def paquete(self): return n.paquete(self.nombre)
    @property
    def variable_url(self): return n.snake(self.nombre).upper() + "_URL"


@dataclass
class Anticorrupcion:
    nombre: str
    origen: str
    interfaz: str
    lenguaje: str
    arquitectura: str
    puerto: int
    integraciones: list[Integracion]

    @property
    def carpeta(self): return "acl-01-anticorrupcion"
    @property
    def paquete(self): return "anticorrupcion"
    @property
    def variable_url(self): return "ACL_URL"


@dataclass
class Sistema:
    proyecto: str
    paquete_base: str
    contextos: list[Contexto]
    acl: Anticorrupcion | None
    advertencias: list[str]
    # id del elemento del diagrama -> {vista, tipo, nombre, archivos: [...]}
    traza: dict[str, dict]

    def contexto(self, nombre: str) -> Contexto:
        return next(c for c in self.contextos if c.nombre == nombre)

    def registrar(self, origen: str, archivo: str):
        """Anota que el elemento `origen` del diagrama produjo `archivo`."""
        if origen in self.traza and archivo not in self.traza[origen]["archivos"]:
            self.traza[origen]["archivos"].append(archivo)

    def a_dict(self):
        return asdict(self)
