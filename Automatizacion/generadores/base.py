"""Clase base de los generadores por lenguaje (patrón Template Method + Strategy).

Cada lenguaje define:
  - LAYOUTS: dónde va cada rol (modelo, puertos, api...) según la arquitectura elegida
  - generar_contexto(): qué archivos produce
Lo común (Jinja, escritura de archivos y trazabilidad) vive aquí.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from archimate import nombres as n
from archimate.modelo import Contexto, Sistema

PLANTILLAS = Path(__file__).resolve().parent.parent / "plantillas"


def entorno(subcarpeta: str) -> Environment:
    env = Environment(loader=FileSystemLoader([str(PLANTILLAS / subcarpeta), str(PLANTILLAS / "comun")]),
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True,
                      keep_trailing_newline=True)
    for nombre in ("snake", "pascal", "camel", "kebab", "paquete", "sin_tildes"):
        env.filters[nombre] = getattr(n, nombre)
    return env


class GeneradorBase(ABC):
    lenguaje: str = ""
    LAYOUTS: dict[str, dict[str, str]] = {}

    def __init__(self, sistema: Sistema, salida: Path):
        self.sistema = sistema
        self.salida = salida
        self.env = entorno(self.lenguaje)

    def layout(self, ctx) -> dict[str, str]:
        return self.LAYOUTS[ctx.arquitectura]

    def escribir(self, relativo: str, plantilla: str, origenes: list[str] = (), **variables) -> Path:
        destino = self.salida / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        texto = self.env.get_template(plantilla).render(sistema=self.sistema, **variables)
        destino.write_text(texto, encoding="utf-8")
        ruta = destino.relative_to(self.salida.parent).as_posix()
        for o in origenes:
            if o:
                self.sistema.registrar(o, ruta)
        return destino

    # ------------------------------------------------------------ comunes
    @staticmethod
    def origenes_contexto(ctx: Contexto) -> list[str]:
        """Todos los elementos del diagrama que influyen en el punto de entrada del contexto."""
        ids = [ctx.origen]
        ids += [r.origen for r in ctx.proveedores + ctx.consumidores]
        return ids

    @abstractmethod
    def generar_contexto(self, ctx: Contexto): ...

    def generar_acl(self, acl):
        raise NotImplementedError(f"La capa anticorrupción todavía no tiene plantillas para {self.lenguaje}")
