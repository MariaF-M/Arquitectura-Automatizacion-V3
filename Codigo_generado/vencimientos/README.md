# Vencimientos

> Generado automáticamente desde el modelo ArchiMate. **No editar a mano lo que se pueda regenerar**: cambie el modelo o `spec.yaml` y vuelva a ejecutar el generador.

| | |
|---|---|
| Dominio (V5) | D-02 — Gestión de vencimientos y priorización |
| Clasificación | CORE |
| Lenguaje | Java 17 |
| Arquitectura | microservicios |
| Puerto | 8002 |
| Base de datos | NoSQL — mongodb |
| Caché | TTL 60 s |
| Campos cifrados | motivo |

**¿Por qué NoSQL?** Las alertas son documentos de vida corta, con semaforización y metadatos que cambian según el tipo de alerta (vencimiento, retiro regulatorio). Se escriben mucho y se consultan por lote o semáforo; un documento por alerta evita joins y permite evolucionar el esquema sin migraciones.

## Agregados (V6)

### AlertaVencimiento
Atributos: `lote_codigo` (texto), `fecha_vencimiento` (fecha), `dias_para_vencer` (entero), `prioridad_fefo` (entero), `semaforo` (texto), `estado` (texto), `motivo` (texto)

| Comando | Evento que emite | Regla |
|---|---|---|
| Evaluar Prioridad FEFO | Prioridad FEFO Calculada | crea el agregado |
| Bloquear Lote Vencido | Lote Bloqueado |  estado → LoteBloqueado; solo desde Activa; requiere motivo |

Invariantes:
- Regla FEFO innegociable: primero se usa lo que vence primero.
- Lotes Vencidos o en Cuarentena no suman al inventario disponible y se bloquean automáticamente (hard stop).

## Componentes y funciones (V5)
- Componente: **Gestión de alertas de vencimiento**
- Función: Prioridad de uso de lotes (FEFO) → `POST /funciones/prioridad-de-uso-de-lotes-fefo` (pendiente)
- Función: Validación de restricciones de uso → `POST /funciones/validacion-de-restricciones-de-uso` (pendiente)
- Función: Notificación de lotes críticos → `POST /funciones/notificacion-de-lotes-criticos` (pendiente)

## Relaciones con otros contextos (V8)
- Consume a **Seguridad y Auditoría** — «Open Host Service»
- Consume a **Inventario** — «Shared Kernel (núcleo compartido: Lote)»
- INT-06 **INVIMA (Vigilancia)** (entrada) a través de ACL-01 — intercambia «OBJ-06 — Alerta regulatoria o retiro de lote»

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | estado del servicio |
| GET | `/eventos` | eventos de dominio publicados |
| GET | `/arquitectura` | componentes, funciones y caché |
| GET | `/alerta-vencimiento` | lista de AlertaVencimiento |
| GET | `/alerta-vencimiento/{id}` | un AlertaVencimiento |
| POST | `/alerta-vencimiento/evaluar-prioridad-fefo` | comando «Evaluar Prioridad FEFO» → evento «Prioridad FEFO Calculada» |
| POST | `/alerta-vencimiento/{id}/bloquear-lote-vencido` | comando «Bloquear Lote Vencido» → evento «Lote Bloqueado» |
| POST | `/alerta-vencimiento/{id}/deshacer` | deshace el último comando (memento) |
| POST | `/funciones/prioridad-de-uso-de-lotes-fefo` | función «Prioridad de uso de lotes (FEFO)» (pendiente, 501) |
| POST | `/funciones/validacion-de-restricciones-de-uso` | función «Validación de restricciones de uso» (pendiente, 501) |
| POST | `/funciones/notificacion-de-lotes-criticos` | función «Notificación de lotes críticos» (pendiente, 501) |

## Ejecutar
```bash
mvn -q package && java -jar target/vencimientos.jar   # el jar incluye el driver de mongodb
```
Por defecto guarda en memoria. Con base de datos real: `PERSISTENCIA=bd` y `BD_URL` (formato del driver:
`mongodb://localhost:27017/vencimientos`). La colección se crea sola al arrancar.

Variables de entorno: `PUERTO`, `PERSISTENCIA` (`memoria` | `bd`), `BD_URL`, `CLAVE_CIFRADO`, `CORS_ORIGENES`, `SEGURIDAD_Y_AUDITORIA_URL`, `INVENTARIO_URL`, `ACL_URL`.
