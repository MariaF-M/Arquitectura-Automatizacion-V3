"""API HTTP de Inventario (adaptador de entrada). Solo biblioteca estándar.

Rutas generadas desde el modelo:
  GET  /salud | /eventos | /arquitectura
  GET  /lote-medicamento            GET /lote-medicamento/{id}
  POST /lote-medicamento/registrar-ingreso      <- comando «Registrar Ingreso»
  POST /lote-medicamento/{id}/descontar-existencias      <- comando «Descontar Existencias»
  POST /lote-medicamento/{id}/deshacer      <- memento
  POST /funciones/control-de-existencias-por-lote      <- función «Control de existencias por lote»
  POST /funciones/gestion-del-estado-del-lote      <- función «Gestión del estado del lote»
  POST /funciones/registros-de-movimientos-del-inventario      <- función «Registros de movimientos del inventario»
"""
from __future__ import annotations

import json
import logging
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from dominio.modelo.errores import NoEncontradoError, ReglaNegocioError
from dominio.servicios.servicios import CasoDeUsoPendiente, COMPONENTES, FUNCIONES
from puertos.entrada.comandos import ManejadorLoteMedicamento, RegistrarIngreso, DescontarExistencias

log = logging.getLogger("api")
# CORS: permite que los microfrontends (otro origen) llamen a esta API
ORIGENES_CORS = os.getenv("CORS_ORIGENES", "*")


def construir_rutas(app) -> list:
    """(método, patrón, función) — `app` trae los manejadores armados en main.py."""
    rutas = [
        ("GET", r"/salud", lambda d: {"contexto": "Inventario", "estado": "ok"}),
        ("GET", r"/eventos", lambda d: app.bus.historial),
        ("GET", r"/arquitectura", lambda d: {
            "contexto": "Inventario", "dominio": "D-01 Gestión de inventario farmacéutico",
            "clasificacion": "CORE", "arquitectura": "hexagonal",
            "componentes": [c.nombre for c in COMPONENTES], "funciones": list(FUNCIONES),
            "cache": {k: {"aciertos": r.aciertos, "fallos": r.fallos} for k, r in app.caches.items()}}),
        ("POST", r"/funciones/(?P<funcion>[\w-]+)", lambda d: _funcion(d)),
    ]
    m_lote_medicamento: ManejadorLoteMedicamento = app.manejadores["lote-medicamento"]
    rutas += [
        ("GET", r"/lote-medicamento", lambda d: m_lote_medicamento.listar()),
        ("GET", r"/lote-medicamento/(?P<id>[\w-]+)", lambda d: m_lote_medicamento.obtener(d["id"])),
        ("POST", r"/lote-medicamento/(?P<id>[\w-]+)/deshacer", lambda d: m_lote_medicamento.deshacer(d["id"])),
        ("POST", r"/lote-medicamento/registrar-ingreso", lambda d: m_lote_medicamento.manejar_registrar_ingreso(RegistrarIngreso(d["cuerpo"]))),
        ("POST", r"/lote-medicamento/(?P<id>[\w-]+)/descontar-existencias", lambda d: m_lote_medicamento.manejar_descontar_existencias(DescontarExistencias(d["cuerpo"], d["id"]))),
    ]
    return [(m, re.compile(p + "$"), f) for m, p, f in rutas]


def _funcion(d):
    clase = FUNCIONES.get(d["funcion"])
    if clase is None:
        raise NoEncontradoError(f"Función {d['funcion']} no existe")
    return clase().ejecutar(d["cuerpo"])


def servidor(app, puerto: int) -> ThreadingHTTPServer:
    rutas = construir_rutas(app)

    class Manejador(BaseHTTPRequestHandler):
        def _responder(self, codigo: int, cuerpo) -> None:
            datos = json.dumps(cuerpo, ensure_ascii=False, default=str).encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(datos)))
            self._cors()
            self.end_headers()
            self.wfile.write(datos)

        def _cors(self) -> None:
            self.send_header("Access-Control-Allow-Origin", ORIGENES_CORS)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

        def do_OPTIONS(self):  # noqa: N802  (preflight CORS)
            self.send_response(204)
            self._cors()
            self.end_headers()

        def _despachar(self, metodo: str) -> None:
            ruta = self.path.split("?")[0].rstrip("/") or "/"
            # se prueban primero las rutas más largas para no confundir /recurso/accion con /recurso/{id}
            for m, patron, funcion in sorted(rutas, key=lambda r: -len(r[1].pattern)):
                coincidencia = patron.match(ruta) if m == metodo else None
                if not coincidencia:
                    continue
                try:
                    largo = int(self.headers.get("Content-Length") or 0)
                    cuerpo = json.loads(self.rfile.read(largo) or b"{}") if largo else {}
                    if not isinstance(cuerpo, dict):
                        return self._responder(400, {"error": "El cuerpo debe ser un objeto JSON, por ejemplo {\"campo\": valor}"})
                    resultado = funcion({**coincidencia.groupdict(), "cuerpo": cuerpo})
                    return self._responder(201 if metodo == "POST" else 200, resultado)
                except ReglaNegocioError as e:
                    return self._responder(422, {"error": str(e)})
                except NoEncontradoError as e:
                    return self._responder(404, {"error": str(e)})
                except CasoDeUsoPendiente as e:
                    return self._responder(501, {"error": str(e)})
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return self._responder(400, {"error": "El cuerpo de la petición no es un JSON válido"})
                except Exception:  # noqa: BLE001 — último recurso: nunca se cae el servidor ni se filtran detalles
                    log.exception("error inesperado en %s %s", metodo, ruta)
                    return self._responder(500, {"error": "Error interno del servidor. El detalle quedó en el log del servicio."})
            self._responder(404, {"error": f"Ruta no encontrada: {metodo} {ruta}"})

        def do_GET(self):  # noqa: N802
            self._despachar("GET")

        def do_POST(self):  # noqa: N802
            self._despachar("POST")

        def log_message(self, formato, *args):
            log.info(formato, *args)

    return ThreadingHTTPServer(("0.0.0.0", puerto), Manejador)
