"""Adaptadores HTTP hacia otros contextos y hacia la ACL. Las URL salen de variables de entorno."""
from __future__ import annotations

import json
import logging
import urllib.request

from dominio.puertos.clientes import PuertoInventario, PuertoAnticorrupcion

log = logging.getLogger("clientes")


class ClienteHttp:
    def __init__(self, url_base: str, timeout: float = 5.0):
        self._url = url_base.rstrip("/")
        self._timeout = timeout

    def get(self, ruta: str):
        with urllib.request.urlopen(self._url + ruta, timeout=self._timeout) as r:
            return json.loads(r.read() or b"null")

    def post(self, ruta: str, datos: dict):
        req = urllib.request.Request(self._url + ruta, data=json.dumps(datos).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self._timeout) as r:
            return json.loads(r.read() or b"null")


class ClienteInventarioHttp(PuertoInventario):
    """Cliente de Inventario (customer-supplier)."""

    def __init__(self, cliente: ClienteHttp):
        self._http = cliente

    def consultar(self, ruta: str):
        return self._http.get(ruta)


class ClienteAnticorrupcionHttp(PuertoAnticorrupcion):
    """Envía datos a la ACL-01, que los traduce al formato del sistema externo."""

    def __init__(self, cliente: ClienteHttp):
        self._http = cliente

    def enviar(self, codigo_integracion: str, datos: dict) -> None:
        try:
            self._http.post(f"/salientes/{codigo_integracion.lower()}", datos)
        except OSError as error:
            log.warning("ACL no disponible para %s: %s", codigo_integracion, error)
