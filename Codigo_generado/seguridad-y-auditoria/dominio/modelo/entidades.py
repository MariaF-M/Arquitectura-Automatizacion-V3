"""Entidades del contexto Seguridad y Auditoría (Data Objects anidados en el componente en V8). Generado automáticamente."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import uuid



@dataclass
class Usuario:
    """Entidad «Usuario» (V8)."""
    usuario: str | None = None
    nombre: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class PerfilRol:
    """Entidad «Perfil / rol» (V8)."""
    nombre: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class RegistroDeAuditoria:
    """Entidad «Registro de auditoría» (V8)."""
    usuario: str | None = None
    accion: str | None = None
    fecha: date | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
