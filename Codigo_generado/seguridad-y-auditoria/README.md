# Seguridad y Auditoría

> Generado automáticamente desde el modelo ArchiMate. **No editar a mano lo que se pueda regenerar**: cambie el modelo o `spec.yaml` y vuelva a ejecutar el generador.

| | |
|---|---|
| Dominio (V5) | D-05 — Seguridad, perfiles, auditoría y notificaciones |
| Clasificación | GENERIC |
| Lenguaje | Python 3.12 |
| Arquitectura | microservicios |
| Puerto | 8005 |
| Base de datos | SQL — postgresql |
| Caché | TTL 120 s |
| Campos cifrados | ninguno |

**¿Por qué SQL?** Usuarios, perfiles y registros de auditoría son datos estructurados que requieren integridad y consultas por usuario, fecha y acción.

## Agregados (V6)

Este dominio no tiene agregados en V6: se generan entidades, servicios y funciones.

## Componentes y funciones (V5)
- Componente: **Gestión de identidades, perfiles y permisos**
- Componente: **Registro de auditoría y trazabilidad de acciones**
- Componente: **Servicio de notificaciones**
- Función: Autenticación y autorización por perfil → `POST /funciones/autenticacion-y-autorizacion-por-perfil` (pendiente)
- Función: Registro de eventos de auditoría → `POST /funciones/registro-de-eventos-de-auditoria` (pendiente)
- Función: Envío de alertas y notificaciones → `POST /funciones/envio-de-alertas-y-notificaciones` (pendiente)

## Relaciones con otros contextos (V8)
- Le sirve a **Abastecimiento** — «Open Host Service»
- Le sirve a **Inventario** — «Open Host Service»
- Le sirve a **Vencimientos** — «Open Host Service»

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | estado del servicio |
| GET | `/eventos` | eventos de dominio publicados |
| GET | `/arquitectura` | componentes, funciones y caché |
| POST | `/funciones/autenticacion-y-autorizacion-por-perfil` | función «Autenticación y autorización por perfil» (pendiente, 501) |
| POST | `/funciones/registro-de-eventos-de-auditoria` | función «Registro de eventos de auditoría» (pendiente, 501) |
| POST | `/funciones/envio-de-alertas-y-notificaciones` | función «Envío de alertas y notificaciones» (pendiente, 501) |

## Ejecutar
```bash
python main.py
```
Por defecto guarda en memoria. Con base de datos real: `PERSISTENCIA=bd` y `BD_URL` (formato del driver:
`postgresql://farmacia:farmacia@localhost:5432/seguridad_y_auditoria`). La tabla se crea sola al arrancar.

Variables de entorno: `PUERTO`, `PERSISTENCIA` (`memoria` | `bd`), `BD_URL`, `CLAVE_CIFRADO`, `CORS_ORIGENES`.
