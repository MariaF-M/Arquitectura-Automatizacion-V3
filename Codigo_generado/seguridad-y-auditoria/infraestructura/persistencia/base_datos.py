"""Adaptador de persistencia para postgresql (SQL). Se activa con PERSISTENCIA=bd.

Justificación de la base de datos (spec.yaml):
  Usuarios, perfiles y registros de auditoría son datos estructurados que requieren
  integridad y consultas por usuario, fecha y acción.

Los campos sensibles [] se guardan cifrados; la base de datos nunca ve el texto plano.
"""
from __future__ import annotations

import os
from datetime import date

import psycopg
from psycopg.rows import dict_row

from infraestructura.transversal.cifrado import Cifrador

CADENA_CONEXION = os.getenv("BD_URL", "postgresql://farmacia:farmacia@localhost:5432/seguridad_y_auditoria")
