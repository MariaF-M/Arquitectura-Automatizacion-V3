"""Puertos de persistencia de Inventario. El dominio depende de estas abstracciones (DIP), no de una base de datos."""
from __future__ import annotations

from abc import ABC, abstractmethod

from dominio.modelo.lote_medicamento import LoteMedicamento


class RepositorioLoteMedicamento(ABC):
    @abstractmethod
    def guardar(self, agregado: LoteMedicamento) -> None: ...

    @abstractmethod
    def obtener(self, id: str) -> LoteMedicamento | None: ...

    @abstractmethod
    def listar(self) -> list[LoteMedicamento]: ...
