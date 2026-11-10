"""Cifrado simple (XOR con clave + Base64) para campos sensibles en reposo.

Es didáctico: en producción se reemplaza por AES (p. ej. con la librería `cryptography`)
sin tocar el dominio, porque solo lo usan los adaptadores de persistencia.
"""
from __future__ import annotations

import base64
import os

PREFIJO = "enc:"


class Cifrador:
    def __init__(self, clave: str | None = None):
        self._clave = (clave or os.getenv("CLAVE_CIFRADO", "farmacia-2026")).encode("utf-8")

    def _xor(self, datos: bytes) -> bytes:
        return bytes(b ^ self._clave[i % len(self._clave)] for i, b in enumerate(datos))

    def cifrar(self, texto: str) -> str:
        return PREFIJO + base64.b64encode(self._xor(texto.encode("utf-8"))).decode("ascii")

    def descifrar(self, texto: str) -> str:
        if not texto.startswith(PREFIJO):
            return texto
        return self._xor(base64.b64decode(texto[len(PREFIJO):])).decode("utf-8")

    def cifrar_campos(self, fila: dict, campos: list[str]) -> dict:
        return {k: self.cifrar(str(v)) if k in campos and v is not None else v for k, v in fila.items()}

    def descifrar_campos(self, fila: dict, campos: list[str]) -> dict:
        return {k: self.descifrar(v) if k in campos and isinstance(v, str) else v for k, v in fila.items()}
