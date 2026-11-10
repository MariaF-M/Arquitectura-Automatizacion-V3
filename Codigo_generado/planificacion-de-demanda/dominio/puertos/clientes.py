"""Puertos hacia otros contextos y hacia la capa anticorrupción (relaciones de V8). Generado automáticamente."""
from __future__ import annotations

from abc import ABC, abstractmethod


class PuertoInventario(ABC):
    """Planificación de Demanda consume a Inventario — patrón «Customer / Supplier» (customer-supplier)."""

    @abstractmethod
    def consultar(self, ruta: str) -> object: ...


class PuertoAnticorrupcion(ABC):
    """Salida hacia sistemas externos, siempre a través de la ACL (V9). Nunca se llama al externo directamente."""

    @abstractmethod
    def enviar(self, codigo_integracion: str, datos: dict) -> None: ...
