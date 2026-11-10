"""Agregado raíz LoteMedicamento del contexto Inventario (D-01).

Generado desde el modelo ArchiMate:
  - Data Object «LoteMedicamento» (V6)  -> esta clase
  - Application Process «Registrar Ingreso» -> método registrar_ingreso() que emite «Lote Ingresado»
  - Application Process «Descontar Existencias» -> método descontar_existencias() que emite «Existencias Descontadas»

Invariantes que protege:
  * La cantidad de existencias nunca puede ser negativa.
  * Todo lote tiene Código, Descripción, Proveedor, Fecha de vencimiento y Registro sanitario desde la recepción técnica.
  * Un lote solo puede estar Disponible, en Cuarentena, Vencido o Bloqueado.
  * No se recibe un lote vencido o que vence hoy (la fecha de vencimiento debe ser posterior a la recepción).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from dominio.modelo.errores import ReglaNegocioError
from dominio.eventos.eventos import EventoDominio, LoteIngresado, ExistenciasDescontadas


CAMPOS = {
    "codigo": str,
    "descripcion": str,
    "proveedor": str,
    "fecha_vencimiento": date,
    "registro_sanitario": str,
    "cantidad": int,
    "estado": str,
}
VALORES_INICIALES = {"estado": "Disponible"}
OBLIGATORIOS = ("codigo", "descripcion", "proveedor", "fecha_vencimiento", "registro_sanitario", )
NO_NEGATIVOS = ("cantidad", )
VALORES_PERMITIDOS = {
    "estado": ["Disponible", "Cuarentena", "Vencido", "Bloqueado"],
}


def _convertir(tipo, valor):
    if valor is None or isinstance(valor, tipo):
        return valor
    if tipo is date:
        return date.fromisoformat(str(valor))
    return tipo(valor)


@dataclass(frozen=True)
class LoteMedicamentoMemento:
    """Memento (GoF): foto inmutable del estado de LoteMedicamento. Solo el agregado sabe crearla y leerla."""
    id: str
    codigo: str | None
    descripcion: str | None
    proveedor: str | None
    fecha_vencimiento: date | None
    registro_sanitario: str | None
    cantidad: int | None
    estado: str | None


class LoteMedicamento:
    def __init__(self, id: str | None = None, **datos):
        self.id = id or str(uuid.uuid4())
        self.codigo: str | None = None
        self.descripcion: str | None = None
        self.proveedor: str | None = None
        self.fecha_vencimiento: date | None = None
        self.registro_sanitario: str | None = None
        self.cantidad: int | None = None
        self.estado: str | None = None
        self._eventos: list[EventoDominio] = []
        self._aplicar({**VALORES_INICIALES, **datos})

    # ----------------------------------------------------------------- comandos (V6)
    @classmethod
    def registrar_ingreso(cls, datos: dict) -> "LoteMedicamento":
        """Comando «Registrar Ingreso»: crea el agregado."""
        agregado = cls(**{k: v for k, v in datos.items() if k != "id"})
        if agregado.fecha_vencimiento is not None and agregado.fecha_vencimiento <= date.today():
            raise ReglaNegocioError("«Registrar Ingreso»: 'fecha_vencimiento' debe ser posterior a hoy")
        agregado.validar()
        agregado._registrar(LoteIngresado(agregado.id, agregado.a_dict()))
        return agregado

    def descontar_existencias(self, datos: dict) -> None:
        """Comando «Descontar Existencias»."""
        if self.estado not in ["Disponible"]:
            raise ReglaNegocioError(f"«Descontar Existencias» no se permite con estado '{self.estado}'")
        if "cantidad" not in datos:
            raise ReglaNegocioError("«Descontar Existencias» requiere 'cantidad'")
        self.cantidad = (self.cantidad or 0) - _convertir(CAMPOS["cantidad"], datos["cantidad"])
        self.validar()
        self._registrar(ExistenciasDescontadas(self.id, self.a_dict()))

    # ----------------------------------------------------------------- invariantes
    def validar(self) -> None:
        for campo in OBLIGATORIOS:
            if getattr(self, campo) in (None, ""):
                raise ReglaNegocioError(f"El campo '{campo}' es obligatorio en LoteMedicamento")
        for campo in NO_NEGATIVOS:
            valor = getattr(self, campo)
            if valor is not None and valor < 0:
                raise ReglaNegocioError(f"'{campo}' no puede ser negativo (valor: {valor})")
        for campo, permitidos in VALORES_PERMITIDOS.items():
            valor = getattr(self, campo)
            if valor is not None and valor not in permitidos:
                raise ReglaNegocioError(f"'{campo}' = '{valor}' no es válido. Permitidos: {permitidos}")

    # ----------------------------------------------------------------- memento
    def crear_memento(self) -> LoteMedicamentoMemento:
        return LoteMedicamentoMemento(self.id, self.codigo, self.descripcion, self.proveedor, self.fecha_vencimiento, self.registro_sanitario, self.cantidad, self.estado)

    def restaurar(self, memento: LoteMedicamentoMemento) -> None:
        self.codigo = memento.codigo
        self.descripcion = memento.descripcion
        self.proveedor = memento.proveedor
        self.fecha_vencimiento = memento.fecha_vencimiento
        self.registro_sanitario = memento.registro_sanitario
        self.cantidad = memento.cantidad
        self.estado = memento.estado

    # ----------------------------------------------------------------- utilidades
    def _aplicar(self, datos: dict) -> None:
        for campo, valor in datos.items():
            if campo in CAMPOS:
                try:
                    setattr(self, campo, _convertir(CAMPOS[campo], valor))
                except (TypeError, ValueError) as error:
                    raise ReglaNegocioError(f"Valor inválido para '{campo}': {valor!r}") from error

    def _registrar(self, evento: EventoDominio) -> None:
        self._eventos.append(evento)

    def extraer_eventos(self) -> list[EventoDominio]:
        eventos, self._eventos = self._eventos, []
        return eventos

    def a_dict(self) -> dict:
        datos = {"id": self.id}
        for campo in CAMPOS:
            valor = getattr(self, campo)
            datos[campo] = valor.isoformat() if isinstance(valor, date) else valor
        return datos

    @classmethod
    def desde_dict(cls, datos: dict) -> "LoteMedicamento":
        return cls(**datos)
