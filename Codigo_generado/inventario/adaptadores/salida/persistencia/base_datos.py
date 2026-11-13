"""Adaptador de persistencia para postgresql (SQL). Se activa con PERSISTENCIA=bd.

Justificación de la base de datos (spec.yaml):
  El inventario exige consistencia fuerte (ACID): una dispensación no puede dejar
  existencias negativas ni dos movimientos pueden pisarse. Los lotes, medicamentos y
  movimientos tienen estructura fija y relaciones claras.

Los campos sensibles ["proveedor"] se guardan cifrados; la base de datos nunca ve el texto plano.
"""
from __future__ import annotations

import os
from datetime import date

import psycopg
from psycopg.rows import dict_row

from adaptadores.salida.transversal.cifrado import Cifrador
from dominio.modelo.lote_medicamento import LoteMedicamento
from puertos.salida.repositorios import RepositorioLoteMedicamento

CADENA_CONEXION = os.getenv("BD_URL", "postgresql://farmacia:farmacia@localhost:5432/inventario")


class RepositorioLoteMedicamentoBaseDatos(RepositorioLoteMedicamento):
    """Tabla «lote_medicamento». Upsert por id; la tabla se crea al arrancar si no existe."""
    TABLA = "lote_medicamento"
    CAMPOS = ["codigo", "descripcion", "proveedor", "fecha_vencimiento", "registro_sanitario", "cantidad", "estado"]
    FECHAS = ["fecha_vencimiento"]
    CAMPOS_CIFRADOS = ["proveedor"]
    DDL = """
    CREATE TABLE IF NOT EXISTS lote_medicamento (
        id VARCHAR(36) PRIMARY KEY,
        codigo VARCHAR(255) NOT NULL UNIQUE,
        descripcion VARCHAR(255) NOT NULL,
        proveedor TEXT NOT NULL,
        fecha_vencimiento DATE NOT NULL,
        registro_sanitario VARCHAR(255) NOT NULL,
        cantidad INTEGER CHECK (cantidad >= 0),
        estado VARCHAR(255) CHECK (estado IN ('Disponible', 'Cuarentena', 'Vencido', 'Bloqueado'))
    )
    """

    def __init__(self, cifrador: Cifrador, cadena: str = CADENA_CONEXION):
        self._cifrador = cifrador
        self._cadena = cadena
        with self._conectar() as conexion:
            conexion.execute(self.DDL)

    def _conectar(self):
        return psycopg.connect(self._cadena, row_factory=dict_row, autocommit=True)

    def guardar(self, agregado: LoteMedicamento) -> None:
        fila = self._cifrador.cifrar_campos(agregado.a_dict(), self.CAMPOS_CIFRADOS)
        for campo in self.FECHAS:
            if fila[campo]:
                fila[campo] = date.fromisoformat(fila[campo])
        columnas = ["id"] + self.CAMPOS
        sql = (f"INSERT INTO {self.TABLA} ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(columnas))}) "
               f"ON CONFLICT (id) DO UPDATE SET {', '.join(f'{c} = EXCLUDED.{c}' for c in self.CAMPOS)}")
        with self._conectar() as conexion:
            conexion.execute(sql, [fila[c] for c in columnas])

    def _desde_fila(self, fila: dict) -> LoteMedicamento:
        return LoteMedicamento.desde_dict(self._cifrador.descifrar_campos(dict(fila), self.CAMPOS_CIFRADOS))

    def obtener(self, id: str) -> LoteMedicamento | None:
        with self._conectar() as conexion:
            fila = conexion.execute(f"SELECT * FROM {self.TABLA} WHERE id = %s", (id,)).fetchone()
        return self._desde_fila(fila) if fila else None

    def listar(self) -> list[LoteMedicamento]:
        with self._conectar() as conexion:
            filas = conexion.execute(f"SELECT * FROM {self.TABLA} ORDER BY id").fetchall()
        return [self._desde_fila(f) for f in filas]
