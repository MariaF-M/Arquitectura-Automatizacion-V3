"""Entidades del contexto Planificación de Demanda (Data Objects anidados en el componente en V8). Generado automáticamente."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import uuid



@dataclass
class Medicamento:
    """Entidad «Medicamento» (V8)."""
    codigo: str | None = None
    principio_activo: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AgendaQuirurgica:
    """Entidad «Agenda quirúrgica» (V8)."""
    procedimiento: str | None = None
    fecha: date | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ConsumoHistorico:
    """Entidad «Consumo histórico» (V8)."""
    medicamento: str | None = None
    periodo: str | None = None
    cantidad: int | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class EstimacionDeDemanda:
    """Entidad «Estimación de demanda» (V8)."""
    medicamento: str | None = None
    cantidad_estimada: int | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
