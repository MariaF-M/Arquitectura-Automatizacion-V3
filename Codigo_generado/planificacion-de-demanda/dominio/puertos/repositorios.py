"""Puertos de persistencia de Planificación de Demanda. El dominio depende de estas abstracciones (DIP), no de una base de datos."""
from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.modelo.estimacion_demanda import EstimacionDemanda


class RepositorioEstimacionDemanda(ABC):
    @abstractmethod
    def guardar(self, agregado: EstimacionDemanda) -> None: ...

    @abstractmethod
    def obtener(self, id: str) -> EstimacionDemanda | None: ...

    @abstractmethod
    def listar(self) -> list[EstimacionDemanda]: ...
