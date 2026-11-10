"""Comandos y sus manejadores (casos de uso de escritura) de Inventario.

Flujo de cada comando:
  1. se carga el agregado y se toma un memento (para deshacer o revertir)
  2. el agregado ejecuta el comando y valida sus invariantes
  3. si falla, se restaura el memento; si no, se guarda y se publican los eventos
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dominio.modelo.errores import NoEncontradoError, ReglaNegocioError
from dominio.memento.memento import Caretaker
from dominio.eventos.bus_eventos import BusEventos
from dominio.modelo.lote_medicamento import LoteMedicamento
from puertos.salida.repositorios import RepositorioLoteMedicamento


@dataclass(frozen=True)
class RegistrarIngreso:
    """Comando «Registrar Ingreso» (Application Process en V6)."""
    datos: dict = field(default_factory=dict)


@dataclass(frozen=True)
class DescontarExistencias:
    """Comando «Descontar Existencias» (Application Process en V6)."""
    datos: dict = field(default_factory=dict)
    id: str = ""


class ManejadorLoteMedicamento:
    def __init__(self, repositorio: RepositorioLoteMedicamento, bus: BusEventos, caretaker: Caretaker):
        self._repo = repositorio
        self._bus = bus
        self._caretaker = caretaker

    def _cargar(self, id: str) -> LoteMedicamento:
        agregado = self._repo.obtener(id)
        if agregado is None:
            raise NoEncontradoError(f"LoteMedicamento {id} no existe")
        return agregado

    def _confirmar(self, agregado: LoteMedicamento) -> dict:
        self._repo.guardar(agregado)
        for evento in agregado.extraer_eventos():
            self._bus.publicar(evento)
        return agregado.a_dict()

    def manejar_registrar_ingreso(self, comando: RegistrarIngreso) -> dict:
        agregado = LoteMedicamento.registrar_ingreso(comando.datos)
        return self._confirmar(agregado)

    def manejar_descontar_existencias(self, comando: DescontarExistencias) -> dict:
        agregado = self._cargar(comando.id)
        memento = agregado.crear_memento()
        try:
            agregado.descontar_existencias(comando.datos)
        except ReglaNegocioError:
            agregado.restaurar(memento)
            raise
        self._caretaker.guardar(agregado.id, memento)
        return self._confirmar(agregado)

    def deshacer(self, id: str) -> dict:
        """Restaura el estado anterior al último comando (patrón Memento)."""
        agregado = self._cargar(id)
        memento = self._caretaker.ultimo(id)
        if memento is None:
            raise ReglaNegocioError("No hay cambios para deshacer")
        agregado.restaurar(memento)
        self._repo.guardar(agregado)
        return agregado.a_dict()

    def obtener(self, id: str) -> dict:
        return self._cargar(id).a_dict()

    def listar(self) -> list[dict]:
        return [a.a_dict() for a in self._repo.listar()]
