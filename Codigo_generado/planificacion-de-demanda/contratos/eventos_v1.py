"""Contratos de Planificación de Demanda: el LENGUAJE PUBLICADO que otros contextos pueden conocer.

Solo tipos primitivos, sin dependencias del dominio y con sufijo V1 para versionarlos.
Un evento de dominio se traduce a su contrato con `a_contrato()` antes de salir del contexto.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class DemandaEstimadaV1:
    """Evento de integración «Demanda Estimada» (versión 1)."""
    evento_id: str
    ocurrido_en: str
    estimacion_demanda_id: str
    medicamento: str | None = None
    periodo: str | None = None
    demanda_programada: int | None = None
    demanda_no_programada: int | None = None
    cantidad_estimada: int | None = None
    estado: str | None = None
    observaciones: str | None = None


@dataclass(frozen=True)
class PrediccionAjustadaV1:
    """Evento de integración «Predicción Ajustada» (versión 1)."""
    evento_id: str
    ocurrido_en: str
    estimacion_demanda_id: str
    medicamento: str | None = None
    periodo: str | None = None
    demanda_programada: int | None = None
    demanda_no_programada: int | None = None
    cantidad_estimada: int | None = None
    estado: str | None = None
    observaciones: str | None = None


def a_contrato(evento) -> dict:
    """Traduce un evento de dominio a su contrato V1 (diccionario listo para publicar)."""
    import uuid
    clase = globals().get(f"{evento.nombre}V1")
    if clase is None:
        return evento.a_dict()
    datos = {k: v for k, v in evento.datos.items() if k != "id" and k in clase.__dataclass_fields__}
    contrato = asdict(clase(str(uuid.uuid4()), evento.ocurrido_en, evento.agregado_id, **datos))
    # Sobre (envelope) común a todos los servicios + el contrato V1
    return {"evento": evento.nombre, "contrato": clase.__name__, "agregado_id": evento.agregado_id,
            "ocurrido_en": evento.ocurrido_en, "datos": contrato}
