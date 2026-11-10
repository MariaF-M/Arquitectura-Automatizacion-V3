"""Caretaker del patrón Memento: guarda el historial de estados por agregado (en memoria)."""
from __future__ import annotations

from collections import defaultdict


class Caretaker:
    def __init__(self, maximo: int = 20):
        self._historial: dict[str, list] = defaultdict(list)
        self._maximo = maximo

    def guardar(self, id: str, memento) -> None:
        pila = self._historial[id]
        pila.append(memento)
        del pila[:-self._maximo]

    def ultimo(self, id: str):
        pila = self._historial.get(id)
        return pila.pop() if pila else None
