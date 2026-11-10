"""Adaptador de persistencia para mongodb (NoSQL). Se activa con PERSISTENCIA=bd.

Justificación de la base de datos (spec.yaml):
  Las estimaciones combinan series históricas y agendas con estructura variable según el
  modelo de predicción; se guardan como documentos versionados y se leen completos para
  análisis.

Los campos sensibles ["observaciones"] se guardan cifrados; la base de datos nunca ve el texto plano.
"""
from __future__ import annotations

import os

from pymongo import MongoClient

from infraestructura.transversal.cifrado import Cifrador
from dominio.modelo.estimacion_demanda import EstimacionDemanda
from dominio.puertos.repositorios import RepositorioEstimacionDemanda

CADENA_CONEXION = os.getenv("BD_URL", "mongodb://localhost:27017/planificacion_de_demanda")


class RepositorioEstimacionDemandaBaseDatos(RepositorioEstimacionDemanda):
    """Colección «estimacion_demanda». Un documento por agregado; _id = id del agregado."""
    COLECCION = "estimacion_demanda"
    CAMPOS_CIFRADOS = ["observaciones"]

    def __init__(self, cifrador: Cifrador, cadena: str = CADENA_CONEXION):
        self._cifrador = cifrador
        self._coleccion = MongoClient(cadena).get_default_database()[self.COLECCION]

    def guardar(self, agregado: EstimacionDemanda) -> None:
        documento = self._cifrador.cifrar_campos(agregado.a_dict(), self.CAMPOS_CIFRADOS)
        documento["_id"] = documento.pop("id")
        self._coleccion.replace_one({"_id": documento["_id"]}, documento, upsert=True)

    def _desde_documento(self, documento: dict) -> EstimacionDemanda:
        documento = dict(documento)
        documento["id"] = documento.pop("_id")
        return EstimacionDemanda.desde_dict(self._cifrador.descifrar_campos(documento, self.CAMPOS_CIFRADOS))

    def obtener(self, id: str) -> EstimacionDemanda | None:
        documento = self._coleccion.find_one({"_id": id})
        return self._desde_documento(documento) if documento else None

    def listar(self) -> list[EstimacionDemanda]:
        return [self._desde_documento(d) for d in self._coleccion.find()]
