"""Servicios de aplicación de Seguridad y Auditoría, uno por Application Component de V5 (D-05),
y casos de uso, uno por Application Function de V5.

Las funciones quedan como punto de extensión: su lógica de negocio no está en el diagrama.
"""
from __future__ import annotations


class CasoDeUsoPendiente(NotImplementedError):
    """La función existe en el diagrama pero su lógica aún no se implementa."""


class AutenticacionYAutorizacionPorPerfil:
    """Application Function «Autenticación y autorización por perfil» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Autenticación y autorización por perfil» está modelada pero su lógica está pendiente")


class RegistroDeEventosDeAuditoria:
    """Application Function «Registro de eventos de auditoría» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Registro de eventos de auditoría» está modelada pero su lógica está pendiente")


class EnvioDeAlertasYNotificaciones:
    """Application Function «Envío de alertas y notificaciones» (V5)."""

    def ejecutar(self, datos: dict) -> dict:
        raise CasoDeUsoPendiente("«Envío de alertas y notificaciones» está modelada pero su lógica está pendiente")


class GestionDeIdentidadesPerfilesYPermisosServicio:
    """Application Component «Gestión de identidades, perfiles y permisos» (V5)."""
    nombre = "Gestión de identidades, perfiles y permisos"


class RegistroDeAuditoriaYTrazabilidadDeAccionesServicio:
    """Application Component «Registro de auditoría y trazabilidad de acciones» (V5)."""
    nombre = "Registro de auditoría y trazabilidad de acciones"


class ServicioDeNotificacionesServicio:
    """Application Component «Servicio de notificaciones» (V5)."""
    nombre = "Servicio de notificaciones"


COMPONENTES = [GestionDeIdentidadesPerfilesYPermisosServicio, RegistroDeAuditoriaYTrazabilidadDeAccionesServicio, ServicioDeNotificacionesServicio]
FUNCIONES = {
    "autenticacion-y-autorizacion-por-perfil": AutenticacionYAutorizacionPorPerfil,
    "registro-de-eventos-de-auditoria": RegistroDeEventosDeAuditoria,
    "envio-de-alertas-y-notificaciones": EnvioDeAlertasYNotificaciones,
}
