"""Entidades del contexto Inventario (Data Objects anidados en el componente en V8). Generado automáticamente."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import uuid

from shared_kernel import Lote  # noqa: F401  (núcleo compartido)



@dataclass
class Medicamento:
    """Entidad «Medicamento» (V8)."""
    codigo: str | None = None
    principio_activo: str | None = None
    concentracion: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class MovimientoDeInventario:
    """Entidad «Movimiento de inventario» (V8)."""
    lote_codigo: str | None = None
    tipo: str | None = None
    cantidad: int | None = None
    fecha: date | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
