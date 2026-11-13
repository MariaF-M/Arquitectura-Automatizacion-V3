"""Punto de entrada de Planificación de Demanda — raíz de composición (aquí se conectan puertos y adaptadores).

Contexto delimitado: Planificación de Demanda  (D-03 Planificación y predicción de demanda — SUPPORTING)
Arquitectura: microservicios   Lenguaje: Python   Puerto: 8003
Relaciones (V8):
  - consume a Inventario: «Customer / Supplier»
  - le sirve a Abastecimiento: «Customer / Supplier»
  - INT-01 Programación quirúrgica (entrada) vía ACL-01

Generado automáticamente desde el modelo ArchiMate. Ejecutar:  python main.py
"""
from __future__ import annotations

import logging
import os
from types import SimpleNamespace

from api.http import servidor
from infraestructura.clientes.http import ClienteHttp, ClienteInventarioHttp, ClienteAnticorrupcionHttp
from aplicacion.memento.memento import Caretaker
from infraestructura.persistencia.cache import RepositorioConCache
from aplicacion.eventos.bus_eventos import BusEventos
from infraestructura.transversal.cifrado import Cifrador
from contratos.eventos_v1 import a_contrato
from aplicacion.comandos.comandos import ManejadorEstimacionDemanda
from infraestructura.persistencia.memoria import RepositorioEstimacionDemandaMemoria


def construir_app() -> SimpleNamespace:
    bus = BusEventos(a_contrato)
    cifrador = Cifrador()
    usar_bd = os.getenv("PERSISTENCIA", "memoria") == "bd"
    if usar_bd:
        from infraestructura.persistencia.base_datos import RepositorioEstimacionDemandaBaseDatos
    app = SimpleNamespace(bus=bus, manejadores={}, caches={}, clientes={})

    repo_estimacion_demanda = RepositorioConCache(
        RepositorioEstimacionDemandaBaseDatos(cifrador) if usar_bd else RepositorioEstimacionDemandaMemoria(cifrador))
    app.caches["estimacion-demanda"] = repo_estimacion_demanda
    app.manejadores["estimacion-demanda"] = ManejadorEstimacionDemanda(repo_estimacion_demanda, bus, Caretaker())

    # customer-supplier: «Customer / Supplier»
    app.clientes["Inventario"] = ClienteInventarioHttp(
        ClienteHttp(os.getenv("INVENTARIO_URL", "http://localhost:8001")))

    acl = ClienteAnticorrupcionHttp(ClienteHttp(os.getenv("ACL_URL", "http://localhost:8010")))
    app.clientes["ACL-01"] = acl
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    puerto = int(os.getenv("PUERTO", "8003"))
    logging.getLogger("main").info("Planificación de Demanda escuchando en el puerto %s", puerto)
    servidor(construir_app(), puerto).serve_forever()
