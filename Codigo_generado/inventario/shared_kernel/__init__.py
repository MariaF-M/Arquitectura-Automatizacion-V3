"""Shared Kernel (núcleo compartido) — relación de V8:
  «Shared Kernel (núcleo compartido: Lote)»: Inventario <-> Vencimientos

Los contextos que lo comparten pueden estar en lenguajes distintos, así que el contrato
canónico es contratos/shared-kernel/*.schema.json; esta clase es su versión en Python.
Cualquier cambio debe acordarse entre los dos equipos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import uuid


@dataclass
class Lote:
    """Entidad compartida «Lote»."""
    codigo: str | None = None
    fecha_vencimiento: date | None = None
    estado: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
