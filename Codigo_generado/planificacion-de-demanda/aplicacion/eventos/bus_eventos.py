"""Bus de eventos en memoria (patrón Observer). Los eventos de dominio se publican aquí."""
from __future__ import annotations

import logging
from collections import defaultdict

log = logging.getLogger("eventos")


class BusEventos:
    def __init__(self, traductor=None):
        # traductor: convierte el evento de dominio a su contrato V1 (lenguaje publicado)
        self._publicar = traductor or (lambda e: e.a_dict())
        self._suscriptores = defaultdict(list)
        self.historial: list[dict] = []

    def suscribir(self, nombre_evento: str, manejador) -> None:
        self._suscriptores[nombre_evento].append(manejador)

    def publicar(self, evento) -> None:
        self.historial.append(self._publicar(evento))
        log.info("evento publicado: %s (%s)", evento.nombre, evento.agregado_id)
        for manejador in self._suscriptores[evento.nombre]:
            try:
                manejador(evento)
            except Exception:  # un suscriptor caído no debe tumbar el comando
                log.exception("fallo el suscriptor de %s", evento.nombre)
