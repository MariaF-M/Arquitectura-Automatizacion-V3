"""Adaptador de persistencia en memoria (por defecto). Cifra en reposo los campos sensibles: ["observaciones"]."""
from __future__ import annotations

from infraestructura.transversal.cifrado import Cifrador
from dominio.modelo.estimacion_demanda import EstimacionDemanda
from dominio.puertos.repositorios import RepositorioEstimacionDemanda


class RepositorioEstimacionDemandaMemoria(RepositorioEstimacionDemanda):
    CAMPOS_CIFRADOS = ["observaciones"]

    def __init__(self, cifrador: Cifrador):
        self._datos: dict[str, dict] = {}
        self._cifrador = cifrador

    def guardar(self, agregado: EstimacionDemanda) -> None:
        self._datos[agregado.id] = self._cifrador.cifrar_campos(agregado.a_dict(), self.CAMPOS_CIFRADOS)

    def obtener(self, id: str) -> EstimacionDemanda | None:
        fila = self._datos.get(id)
        return EstimacionDemanda.desde_dict(self._cifrador.descifrar_campos(fila, self.CAMPOS_CIFRADOS)) if fila else None

    def listar(self) -> list[EstimacionDemanda]:
        return [self.obtener(i) for i in self._datos]
