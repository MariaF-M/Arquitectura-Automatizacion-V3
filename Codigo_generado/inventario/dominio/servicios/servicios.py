"""Servicios de aplicación de Inventario, uno por Application Component de V5 (D-01),
y casos de uso, uno por Application Function de V5.

Las funciones quedan como punto de extensión: su lógica de negocio no está en el diagrama.
"""
from __future__ import annotations


class CasoDeUsoPendiente(NotImplementedError):
    """La función existe en el diagrama pero su lógica aún no se implementa."""


class ControlDeExistenciasPorLote:
    """Application Function «Control de existencias por lote» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Control de existencias por lote» está modelada pero su lógica está pendiente")


class GestionDelEstadoDelLote:
    """Application Function «Gestión del estado del lote» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Gestión del estado del lote» está modelada pero su lógica está pendiente")


class RegistrosDeMovimientosDelInventario:
    """Application Function «Registros de movimientos del inventario» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Registros de movimientos del inventario» está modelada pero su lógica está pendiente")


class GestionDeMedicamentosServicio:
    """Application Component «Gestión de medicamentos» (V5)."""
    nombre = "Gestión de medicamentos"


class GestionDeLotesDeMedicamentosServicio:
    """Application Component «Gestión de lotes de medicamentos» (V5)."""
    nombre = "Gestión de lotes de medicamentos"


COMPONENTES = [GestionDeMedicamentosServicio, GestionDeLotesDeMedicamentosServicio]
FUNCIONES = {
    "control-de-existencias-por-lote": ControlDeExistenciasPorLote,
    "gestion-del-estado-del-lote": GestionDelEstadoDelLote,
    "registros-de-movimientos-del-inventario": RegistrosDeMovimientosDelInventario,
}
