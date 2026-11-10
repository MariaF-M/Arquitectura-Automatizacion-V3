# Abastecimiento

> Generado automáticamente desde el modelo ArchiMate. **No editar a mano lo que se pueda regenerar**: cambie el modelo o `spec.yaml` y vuelva a ejecutar el generador.

| | |
|---|---|
| Dominio (V5) | D-04 — Abastecimiento y requerimientos de compra |
| Clasificación | SUPPORTING |
| Lenguaje | C# / .NET 8 |
| Arquitectura | hexagonal |
| Puerto | 8004 |
| Base de datos | SQL — postgresql |
| Caché | TTL 30 s |
| Campos cifrados | autorizado_por |

**¿Por qué SQL?** Un requerimiento pasa por estados controlados (sugerido, autorizado) y debe quedar auditable ante Compras/ERP; se necesita integridad referencial y transacciones.

## Agregados (V6)

### RequerimientoCompra
Atributos: `principio_activo` (texto), `concentracion` (texto), `cantidad` (entero), `nivel_urgencia` (texto), `estado` (texto), `autorizado_por` (texto)

| Comando | Evento que emite | Regla |
|---|---|---|
| Generar Requisición | Requisición Sugerida | crea el agregado |
| Autorizar Requisición | Requerimiento Autorizado |  estado → Autorizado; solo desde Sugerido; requiere autorizado_por |

Invariantes:
- El requerimiento contiene principio activo (DCI), concentración, cantidad y nivel de urgencia.
- Ningún requerimiento viaja a Compras (ERP) sin autorización técnica previa del Químico Farmacéutico.

## Componentes y funciones (V5)
- Componente: **Gestión de requerimientos de compra**
- Componente: **Gestión de autorización técnica**
- Función: Seguimiento del abastecimiento → `POST /funciones/seguimiento-del-abastecimiento` (pendiente)
- Función: Cálculo de cantidad requerida → `POST /funciones/calculo-de-cantidad-requerida` (pendiente)

## Relaciones con otros contextos (V8)
- Consume a **Planificación de Demanda** — «Customer / Supplier»
- Consume a **Seguridad y Auditoría** — «Open Host Service»
- Consume a **Inventario** — «Customer / Supplier»
- INT-04 **Sistema ERP (Compras)** (salida) a través de ACL-01 — intercambia «OBJ-04 — Requerimiento y estado de compra»

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | estado del servicio |
| GET | `/eventos` | eventos de dominio publicados |
| GET | `/arquitectura` | componentes, funciones y caché |
| GET | `/requerimiento-compra` | lista de RequerimientoCompra |
| GET | `/requerimiento-compra/{id}` | un RequerimientoCompra |
| POST | `/requerimiento-compra/generar-requisicion` | comando «Generar Requisición» → evento «Requisición Sugerida» |
| POST | `/requerimiento-compra/{id}/autorizar-requisicion` | comando «Autorizar Requisición» → evento «Requerimiento Autorizado» |
| POST | `/requerimiento-compra/{id}/deshacer` | deshace el último comando (memento) |
| POST | `/funciones/seguimiento-del-abastecimiento` | función «Seguimiento del abastecimiento» (pendiente, 501) |
| POST | `/funciones/calculo-de-cantidad-requerida` | función «Cálculo de cantidad requerida» (pendiente, 501) |

## Ejecutar
```bash
dotnet run
```
Por defecto guarda en memoria. Con base de datos real: `PERSISTENCIA=bd` y `BD_URL` (formato del driver:
`Host=localhost;Database=abastecimiento;Username=farmacia;Password=farmacia`). La tabla se crea sola al arrancar.

Variables de entorno: `PUERTO`, `PERSISTENCIA` (`memoria` | `bd`), `BD_URL`, `CLAVE_CIFRADO`, `CORS_ORIGENES`, `PLANIFICACION_DE_DEMANDA_URL`, `SEGURIDAD_Y_AUDITORIA_URL`, `INVENTARIO_URL`, `ACL_URL`.
