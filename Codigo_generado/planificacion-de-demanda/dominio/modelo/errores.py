"""Errores del dominio de Planificación de Demanda. Generado automáticamente."""


class ReglaNegocioError(Exception):
    """Se viola una invariante del agregado (ver spec.yaml / V6)."""


class NoEncontradoError(Exception):
    """El agregado solicitado no existe."""
