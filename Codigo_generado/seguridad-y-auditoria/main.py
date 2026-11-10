"""Punto de entrada de Seguridad y Auditoría — raíz de composición (aquí se conectan puertos y adaptadores).

Contexto delimitado: Seguridad y Auditoría  (D-05 Seguridad, perfiles, auditoría y notificaciones — GENERIC)
Arquitectura: microservicios   Lenguaje: Python   Puerto: 8005
Relaciones (V8):
  - le sirve a Abastecimiento: «Open Host Service»
  - le sirve a Inventario: «Open Host Service»
  - le sirve a Vencimientos: «Open Host Service»

Generado automáticamente desde el modelo ArchiMate. Ejecutar:  python main.py
"""
from __future__ import annotations

import logging
import os
from types import SimpleNamespace

from api.http import servidor
from infraestructura.clientes.http import ClienteHttp
from aplicacion.memento.memento import Caretaker
from infraestructura.persistencia.cache import RepositorioConCache
from aplicacion.eventos.bus_eventos import BusEventos
from infraestructura.transversal.cifrado import Cifrador
from contratos.eventos_v1 import a_contrato


def construir_app() -> SimpleNamespace:
    bus = BusEventos(a_contrato)
    cifrador = Cifrador()
    usar_bd = os.getenv("PERSISTENCIA", "memoria") == "bd"
    app = SimpleNamespace(bus=bus, manejadores={}, caches={}, clientes={})
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    puerto = int(os.getenv("PUERTO", "8005"))
    logging.getLogger("main").info("Seguridad y Auditoría escuchando en el puerto %s", puerto)
    servidor(construir_app(), puerto).serve_forever()
