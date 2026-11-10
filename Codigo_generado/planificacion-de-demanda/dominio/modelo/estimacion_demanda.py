"""Agregado raíz EstimacionDemanda del contexto Planificación de Demanda (D-03).

Generado desde el modelo ArchiMate:
  - Data Object «EstimacionDemanda» (V6)  -> esta clase
  - Application Process «Calcular Demanda» -> método calcular_demanda() que emite «Demanda Estimada»
  - Application Process «Ajustar Predicción» -> método ajustar_prediccion() que emite «Predicción Ajustada»

Invariantes que protege:
  * La estimación considera demanda programada (cirugías, censo) y no programada (histórico de urgencias).
  * Toda predicción es una sugerencia que un humano debe validar antes de pasar a abastecimiento.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from dominio.modelo.errores import ReglaNegocioError
from dominio.eventos.eventos import EventoDominio, DemandaEstimada, PrediccionAjustada


CAMPOS = {
    "medicamento": str,
    "periodo": str,
    "demanda_programada": int,
    "demanda_no_programada": int,
    "cantidad_estimada": int,
    "estado": str,
    "observaciones": str,
}
VALORES_INICIALES = {"estado": "Sugerida"}
OBLIGATORIOS = ("medicamento", "periodo", )
NO_NEGATIVOS = ("demanda_programada", "demanda_no_programada", "cantidad_estimada", )
VALORES_PERMITIDOS = {
    "estado": ["Sugerida", "Ajustada", "Validada"],
}


def _convertir(tipo, valor):
    if valor is None or isinstance(valor, tipo):
        return valor
    if tipo is date:
        return date.fromisoformat(str(valor))
    return tipo(valor)


@dataclass(frozen=True)
class EstimacionDemandaMemento:
    """Memento (GoF): foto inmutable del estado de EstimacionDemanda. Solo el agregado sabe crearla y leerla."""
    id: str
    medicamento: str | None
    periodo: str | None
    demanda_programada: int | None
    demanda_no_programada: int | None
    cantidad_estimada: int | None
    estado: str | None
    observaciones: str | None


class EstimacionDemanda:
    def __init__(self, id: str | None = None, **datos):
        self.id = id or str(uuid.uuid4())
        self.medicamento: str | None = None
        self.periodo: str | None = None
        self.demanda_programada: int | None = None
        self.demanda_no_programada: int | None = None
        self.cantidad_estimada: int | None = None
        self.estado: str | None = None
        self.observaciones: str | None = None
        self._eventos: list[EventoDominio] = []
        self._aplicar({**VALORES_INICIALES, **datos})

    # ----------------------------------------------------------------- comandos (V6)
    @classmethod
    def calcular_demanda(cls, datos: dict) -> "EstimacionDemanda":
        """Comando «Calcular Demanda»: crea el agregado."""
        agregado = cls(**{k: v for k, v in datos.items() if k != "id"})
        agregado.validar()
        agregado._registrar(DemandaEstimada(agregado.id, agregado.a_dict()))
        return agregado

    def ajustar_prediccion(self, datos: dict) -> None:
        """Comando «Ajustar Predicción»."""
        if datos.get("observaciones") in (None, ""):
            raise ReglaNegocioError("«Ajustar Predicción» requiere 'observaciones'")
        self._aplicar({k: v for k, v in datos.items() if k != "id"})
        self.estado = "Ajustada"
        self.validar()
        self._registrar(PrediccionAjustada(self.id, self.a_dict()))

    # ----------------------------------------------------------------- invariantes
    def validar(self) -> None:
        for campo in OBLIGATORIOS:
            if getattr(self, campo) in (None, ""):
                raise ReglaNegocioError(f"El campo '{campo}' es obligatorio en EstimacionDemanda")
        for campo in NO_NEGATIVOS:
            valor = getattr(self, campo)
            if valor is not None and valor < 0:
                raise ReglaNegocioError(f"'{campo}' no puede ser negativo (valor: {valor})")
        for campo, permitidos in VALORES_PERMITIDOS.items():
            valor = getattr(self, campo)
            if valor is not None and valor not in permitidos:
                raise ReglaNegocioError(f"'{campo}' = '{valor}' no es válido. Permitidos: {permitidos}")

    # ----------------------------------------------------------------- memento
    def crear_memento(self) -> EstimacionDemandaMemento:
        return EstimacionDemandaMemento(self.id, self.medicamento, self.periodo, self.demanda_programada, self.demanda_no_programada, self.cantidad_estimada, self.estado, self.observaciones)

    def restaurar(self, memento: EstimacionDemandaMemento) -> None:
        self.medicamento = memento.medicamento
        self.periodo = memento.periodo
        self.demanda_programada = memento.demanda_programada
        self.demanda_no_programada = memento.demanda_no_programada
        self.cantidad_estimada = memento.cantidad_estimada
        self.estado = memento.estado
        self.observaciones = memento.observaciones

    # ----------------------------------------------------------------- utilidades
    def _aplicar(self, datos: dict) -> None:
        for campo, valor in datos.items():
            if campo in CAMPOS:
                try:
                    setattr(self, campo, _convertir(CAMPOS[campo], valor))
                except (TypeError, ValueError) as error:
                    raise ReglaNegocioError(f"Valor inválido para '{campo}': {valor!r}") from error

    def _registrar(self, evento: EventoDominio) -> None:
        self._eventos.append(evento)

    def extraer_eventos(self) -> list[EventoDominio]:
        eventos, self._eventos = self._eventos, []
        return eventos

    def a_dict(self) -> dict:
        datos = {"id": self.id}
        for campo in CAMPOS:
            valor = getattr(self, campo)
            datos[campo] = valor.isoformat() if isinstance(valor, date) else valor
        return datos

    @classmethod
    def desde_dict(cls, datos: dict) -> "EstimacionDemanda":
        return cls(**datos)
