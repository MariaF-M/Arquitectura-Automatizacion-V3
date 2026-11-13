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

import re
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
OBLIGATORIOS = ("medicamento", "periodo", "demanda_programada", )
NO_NEGATIVOS = ("demanda_programada", "demanda_no_programada", "cantidad_estimada", )
VALORES_PERMITIDOS = {
    "estado": ["Sugerida", "Ajustada", "Validada"],
}


# Reglas de formato por atributo (spec.yaml -> formatos): patrón, rango y largo máximo
FORMATOS = {
    "medicamento": {"patron": '^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .,()/-]{3,100}$', "mensaje": 'debe tener entre 3 y 100 caracteres (letras, números y signos básicos)', "minimo": None, "maximo": None, "max_largo": 255},
    "periodo": {"patron": '^[0-9]{4}-(0[1-9]|1[0-2])$', "mensaje": 'debe tener el formato AAAA-MM (ej: 2026-12)', "minimo": None, "maximo": None, "max_largo": 255},
    "demanda_programada": {"patron": None, "mensaje": None, "minimo": 0, "maximo": 1000000, "max_largo": None},
    "demanda_no_programada": {"patron": None, "mensaje": None, "minimo": 0, "maximo": 1000000, "max_largo": None},
    "cantidad_estimada": {"patron": None, "mensaje": None, "minimo": 0, "maximo": 1000000, "max_largo": None},
    "estado": {"patron": None, "mensaje": None, "minimo": None, "maximo": None, "max_largo": 255},
    "observaciones": {"patron": None, "mensaje": None, "minimo": None, "maximo": None, "max_largo": 500},
}


def _convertir(tipo, valor):
    """Convierte un valor recibido al tipo del atributo. Lanza ValueError si no se puede."""
    if valor is None:
        return None
    if tipo is str:
        texto = str(valor).strip()          # se ignoran espacios al inicio y al final
        return texto or None                # "   " cuenta como vacío
    if isinstance(valor, str) and not valor.strip():
        return None
    if tipo is bool:
        if isinstance(valor, bool):
            return valor
        if str(valor).strip().lower() in ("true", "false"):
            return str(valor).strip().lower() == "true"
        raise ValueError("se esperaba true o false")
    if isinstance(valor, bool):              # True/False no son números válidos
        raise ValueError("se esperaba un número")
    if tipo is int:
        if isinstance(valor, float) and not valor.is_integer():
            raise ValueError("se esperaba un número entero")
        return int(str(valor).strip()) if isinstance(valor, str) else int(valor)
    if tipo is float:
        return float(str(valor).strip().replace(",", ".")) if isinstance(valor, str) else float(valor)
    if tipo is date:
        return valor if isinstance(valor, date) else date.fromisoformat(str(valor).strip())
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
        for campo, regla in FORMATOS.items():
            valor = getattr(self, campo)
            if valor is None:
                continue
            if isinstance(valor, str):
                if regla["max_largo"] and len(valor) > regla["max_largo"]:
                    raise ReglaNegocioError(f"'{campo}' admite máximo {regla['max_largo']} caracteres")
                if regla["patron"] and not re.fullmatch(regla["patron"], valor):
                    raise ReglaNegocioError(f"'{campo}' {regla['mensaje']} (recibido: '{valor}')")
            else:
                if regla["minimo"] is not None and valor < regla["minimo"]:
                    raise ReglaNegocioError(f"'{campo}' debe ser mayor o igual a {regla['minimo']:g} (recibido: {valor})")
                if regla["maximo"] is not None and valor > regla["maximo"]:
                    raise ReglaNegocioError(f"'{campo}' debe ser menor o igual a {regla['maximo']:g} (recibido: {valor})")

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
                    esperado = {"int": "un número entero", "float": "un número", "date": "una fecha AAAA-MM-DD",
                                "bool": "true o false", "str": "un texto"}[CAMPOS[campo].__name__]
                    raise ReglaNegocioError(f"Valor inválido para '{campo}': {valor!r} (se esperaba {esperado})") from error

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
