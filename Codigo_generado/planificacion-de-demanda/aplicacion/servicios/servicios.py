"""Servicios de aplicación de Planificación de Demanda, uno por Application Component de V5 (D-03),
y casos de uso, uno por Application Function de V5.

Las funciones quedan como punto de extensión: su lógica de negocio no está en el diagrama.
"""
from __future__ import annotations


class CasoDeUsoPendiente(NotImplementedError):
    """La función existe en el diagrama pero su lógica aún no se implementa."""


class PrediccionDeDemanda:
    """Application Function «Predicción de demanda» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Predicción de demanda» está modelada pero su lógica está pendiente")


class GestionDeConsumoHistoricoServicio:
    """Application Component «Gestión de consumo histórico» (V5)."""
    nombre = "Gestión de consumo histórico"


class GestionDeProgramacionHospitalariaServicio:
    """Application Component «Gestión de programación hospitalaria» (V5)."""
    nombre = "Gestión de programación hospitalaria"


class CalculoDeNecesidadEstimadaDeMedicamentosServicio:
    """Application Component «Cálculo de necesidad estimada de medicamentos» (V5)."""
    nombre = "Cálculo de necesidad estimada de medicamentos"


COMPONENTES = [GestionDeConsumoHistoricoServicio, GestionDeProgramacionHospitalariaServicio, CalculoDeNecesidadEstimadaDeMedicamentosServicio]
FUNCIONES = {
    "prediccion-de-demanda": PrediccionDeDemanda,
}
