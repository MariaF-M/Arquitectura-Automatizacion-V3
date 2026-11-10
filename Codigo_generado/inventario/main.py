"""Punto de entrada de Inventario — raíz de composición (aquí se conectan puertos y adaptadores).

Contexto delimitado: Inventario  (D-01 Gestión de inventario farmacéutico — CORE)
Arquitectura: hexagonal   Lenguaje: Python   Puerto: 8001
Relaciones (V8):
  - consume a Seguridad y Auditoría: «Open Host Service»
  - le sirve a Abastecimiento: «Customer / Supplier»
  - le sirve a Planificación de Demanda: «Customer / Supplier»
  - le sirve a Vencimientos: «Shared Kernel (núcleo compartido: Lote)»
  - INT-02 Historia clínica electrónica (entrada) vía ACL-01
  - INT-03 Servicio de urgencias (entrada) vía ACL-01
  - INT-05 Proveedor de medicamentos (entrada) vía ACL-01

Generado automáticamente desde el modelo ArchiMate. Ejecutar:  python main.py
"""
from __future__ import annotations

import logging
import os
from types import SimpleNamespace

from adaptadores.entrada.http import servidor
from adaptadores.salida.clientes.http import ClienteHttp, ClienteSeguridadYAuditoriaHttp, ClienteAnticorrupcionHttp
from dominio.memento.memento import Caretaker
from adaptadores.salida.persistencia.cache import RepositorioConCache
from dominio.eventos.bus_eventos import BusEventos
from adaptadores.salida.transversal.cifrado import Cifrador
from contratos.eventos_v1 import a_contrato
from puertos.entrada.comandos import ManejadorLoteMedicamento
from adaptadores.salida.persistencia.memoria import RepositorioLoteMedicamentoMemoria
from adaptadores.salida.persistencia.base_datos import RepositorioLoteMedicamentoBaseDatos


def construir_app() -> SimpleNamespace:
    bus = BusEventos(a_contrato)
    cifrador = Cifrador()
    usar_bd = os.getenv("PERSISTENCIA", "memoria") == "bd"
    app = SimpleNamespace(bus=bus, manejadores={}, caches={}, clientes={})

    repo_lote_medicamento = RepositorioConCache(
        RepositorioLoteMedicamentoBaseDatos(cifrador) if usar_bd else RepositorioLoteMedicamentoMemoria(cifrador))
    app.caches["lote-medicamento"] = repo_lote_medicamento
    app.manejadores["lote-medicamento"] = ManejadorLoteMedicamento(repo_lote_medicamento, bus, Caretaker())

    # open-host-service: «Open Host Service»
    app.clientes["Seguridad y Auditoría"] = ClienteSeguridadYAuditoriaHttp(
        ClienteHttp(os.getenv("SEGURIDAD_Y_AUDITORIA_URL", "http://localhost:8005")))

    acl = ClienteAnticorrupcionHttp(ClienteHttp(os.getenv("ACL_URL", "http://localhost:8010")))
    app.clientes["ACL-01"] = acl
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    puerto = int(os.getenv("PUERTO", "8001"))
    logging.getLogger("main").info("Inventario escuchando en el puerto %s", puerto)
    servidor(construir_app(), puerto).serve_forever()
