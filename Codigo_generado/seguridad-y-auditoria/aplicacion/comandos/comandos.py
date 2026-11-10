"""Comandos y sus manejadores (casos de uso de escritura) de Seguridad y Auditoría.

Flujo de cada comando:
  1. se carga el agregado y se toma un memento (para deshacer o revertir)
  2. el agregado ejecuta el comando y valida sus invariantes
  3. si falla, se restaura el memento; si no, se guarda y se publican los eventos
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dominio.modelo.errores import NoEncontradoError, ReglaNegocioError
from aplicacion.memento.memento import Caretaker
from aplicacion.eventos.bus_eventos import BusEventos
