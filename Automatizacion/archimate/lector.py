"""Lectura de bajo nivel de un modelo .archimate (formato nativo de Archi).

Solo sabe de elementos, relaciones y vistas; no sabe nada de DDD.
La interpretación (contextos, agregados, etc.) la hace `extractor.py`.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"


@dataclass(frozen=True)
class Elemento:
    id: str
    tipo: str          # p. ej. ApplicationComponent, DataObject
    nombre: str
    documentacion: str = ""


@dataclass(frozen=True)
class Relacion:
    id: str
    tipo: str          # p. ej. Serving, Flow, Triggering, Access, Composition
    origen: str        # id del elemento origen
    destino: str       # id del elemento destino
    nombre: str = ""


@dataclass
class NodoVista:
    """Un elemento (o grupo visual) dibujado en una vista, con sus hijos anidados."""
    elemento: Elemento | None      # None si es un grupo visual o nota
    etiqueta: str                  # nombre del grupo/nota cuando elemento es None
    hijos: list["NodoVista"] = field(default_factory=list)
    conexiones: list[Relacion] = field(default_factory=list)  # relaciones que salen de este nodo en la vista

    def recorrer(self):
        yield self
        for h in self.hijos:
            yield from h.recorrer()


@dataclass
class Vista:
    id: str
    nombre: str
    raiz: list[NodoVista]

    def nodos(self):
        for n in self.raiz:
            yield from n.recorrer()

    def elementos(self, tipo: str | None = None) -> list[Elemento]:
        vistos, salida = set(), []
        for n in self.nodos():
            e = n.elemento
            if e and (tipo is None or e.tipo == tipo) and e.id not in vistos:
                vistos.add(e.id)
                salida.append(e)
        return salida

    def relaciones(self) -> list[Relacion]:
        return [r for n in self.nodos() for r in n.conexiones]


class ModeloArchimate:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)
        raiz = ET.parse(self.ruta).getroot()
        self.nombre = raiz.get("name", "")
        self.elementos: dict[str, Elemento] = {}
        self.relaciones: dict[str, Relacion] = {}
        xml_vistas = []
        for e in raiz.iter("element"):
            tipo = (e.get(XSI_TYPE) or "").replace("archimate:", "")
            nombre = (e.get("name") or "").strip()
            doc = (e.findtext("documentation") or "").strip()
            if tipo == "ArchimateDiagramModel":
                xml_vistas.append(e)
            elif tipo.endswith("Relationship"):
                self.relaciones[e.get("id")] = Relacion(
                    e.get("id"), tipo.removesuffix("Relationship"),
                    e.get("source"), e.get("target"), nombre)
            else:
                self.elementos[e.get("id")] = Elemento(e.get("id"), tipo, nombre, doc)
        self.vistas: dict[str, Vista] = {}
        for v in xml_vistas:
            vista = Vista(v.get("id"), v.get("name").strip(), [self._nodo(c) for c in v.findall("child")])
            self.vistas[vista.nombre] = vista

    def _nodo(self, xml) -> NodoVista:
        ref = xml.get("archimateElement")
        elemento = self.elementos.get(ref) if ref else None
        etiqueta = (xml.get("name") or xml.findtext("content") or "").strip()
        nodo = NodoVista(elemento, etiqueta)
        for sc in xml.findall("sourceConnection"):
            rel = self.relaciones.get(sc.get("archimateRelationship") or "")
            if rel:
                nodo.conexiones.append(rel)
        nodo.hijos = [self._nodo(c) for c in xml.findall("child")]
        return nodo

    def vista(self, nombre: str) -> Vista:
        if nombre in self.vistas:
            return self.vistas[nombre]
        # tolera diferencias menores (espacios, guiones)
        for k, v in self.vistas.items():
            if k.lower().startswith(nombre.lower()):
                return v
        raise KeyError(f"No existe la vista '{nombre}'. Vistas disponibles: {list(self.vistas)}")

    def relaciones_de(self, elemento_id: str, tipo: str | None = None, sentido: str = "salida"):
        for r in self.relaciones.values():
            if tipo and r.tipo != tipo:
                continue
            if (sentido == "salida" and r.origen == elemento_id) or (sentido == "entrada" and r.destino == elemento_id):
                yield r
