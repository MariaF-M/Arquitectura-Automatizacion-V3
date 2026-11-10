"""Errores del dominio de Inventario. Generado automáticamente."""


class ReglaNegocioError(Exception):
    """Se viola una invariante del agregado (ver spec.yaml / V6)."""


class NoEncontradoError(Exception):
    """El agregado solicitado no existe."""
