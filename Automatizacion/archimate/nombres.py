"""Conversión de nombres del diagrama (español, con tildes y espacios) a identificadores de código."""
import re
import unicodedata

_STOP = {"de", "del", "la", "las", "el", "los", "y", "e", "por", "para", "en", "a", "con"}


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def palabras(texto: str) -> list[str]:
    texto = sin_tildes(texto)
    texto = re.sub(r"([a-z])([A-Z])", r"\1 \2", texto)  # LoteMedicamento -> Lote Medicamento
    return [p for p in re.split(r"[^A-Za-z0-9]+", texto) if p]


def pascal(texto: str) -> str:
    return "".join(p[:1].upper() + p[1:].lower() for p in palabras(texto))


def camel(texto: str) -> str:
    p = pascal(texto)
    return p[:1].lower() + p[1:]


def snake(texto: str) -> str:
    return "_".join(p.lower() for p in palabras(texto))


def kebab(texto: str) -> str:
    return "-".join(p.lower() for p in palabras(texto))


def paquete(texto: str) -> str:
    """Identificador válido como paquete Java (minúsculas, sin separadores)."""
    return "".join(p.lower() for p in palabras(texto))


def raices(texto: str) -> set[str]:
    """Raíces de 6 letras de las palabras significativas (para emparejar nombres parecidos)."""
    return {p.lower()[:6] for p in palabras(texto) if p.lower() not in _STOP and not p.isdigit() and len(p) > 2}
