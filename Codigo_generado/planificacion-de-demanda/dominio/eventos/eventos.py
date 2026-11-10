"""Eventos de dominio de Planificación de Demanda (Application Events de V6). Generado automáticamente."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class EventoDominio:
    agregado_id: str
    datos: dict
    ocurrido_en: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def nombre(self) -> str:
        return type(self).__name__

    def a_dict(self) -> dict:
        return {"evento": self.nombre, "agregado_id": self.agregado_id, "datos": self.datos, "ocurrido_en": self.ocurrido_en}


class DemandaEstimada(EventoDominio):
    """Evento «Demanda Estimada» del agregado EstimacionDemanda."""


class PrediccionAjustada(EventoDominio):
    """Evento «Predicción Ajustada» del agregado EstimacionDemanda."""
