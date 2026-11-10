"""Adaptador de persistencia en memoria (por defecto). Cifra en reposo los campos sensibles: ["proveedor"]."""
from __future__ import annotations

from adaptadores.salida.transversal.cifrado import Cifrador
from dominio.modelo.lote_medicamento import LoteMedicamento
from puertos.salida.repositorios import RepositorioLoteMedicamento


class RepositorioLoteMedicamentoMemoria(RepositorioLoteMedicamento):
    CAMPOS_CIFRADOS = ["proveedor"]

    def __init__(self, cifrador: Cifrador):
        self._datos: dict[str, dict] = {}
        self._cifrador = cifrador

    def guardar(self, agregado: LoteMedicamento) -> None:
        self._datos[agregado.id] = self._cifrador.cifrar_campos(agregado.a_dict(), self.CAMPOS_CIFRADOS)

    def obtener(self, id: str) -> LoteMedicamento | None:
        fila = self._datos.get(id)
        return LoteMedicamento.desde_dict(self._cifrador.descifrar_campos(fila, self.CAMPOS_CIFRADOS)) if fila else None

    def listar(self) -> list[LoteMedicamento]:
        return [self.obtener(i) for i in self._datos]
