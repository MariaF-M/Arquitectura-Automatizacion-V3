# Inventario

> Generado automáticamente desde el modelo ArchiMate. **No editar a mano lo que se pueda regenerar**: cambie el modelo o `spec.yaml` y vuelva a ejecutar el generador.

| | |
|---|---|
| Dominio (V5) | D-01 — Gestión de inventario farmacéutico |
| Clasificación | CORE |
| Lenguaje | Python 3.12 |
| Arquitectura | hexagonal |
| Puerto | 8001 |
| Base de datos | SQL — postgresql |
| Caché | TTL 30 s |
| Campos cifrados | proveedor |

**¿Por qué SQL?** El inventario exige consistencia fuerte (ACID): una dispensación no puede dejar existencias negativas ni dos movimientos pueden pisarse. Los lotes, medicamentos y movimientos tienen estructura fija y relaciones claras.

## Agregados (V6)

### LoteMedicamento
Atributos: `codigo` (texto), `descripcion` (texto), `proveedor` (texto), `fecha_vencimiento` (fecha), `registro_sanitario` (texto), `cantidad` (entero), `estado` (texto)

| Comando | Evento que emite | Regla |
|---|---|---|
| Registrar Ingreso | Lote Ingresado | crea el agregado |
| Descontar Existencias | Existencias Descontadas | resta `cantidad`; solo desde Disponible |

Invariantes:
- La cantidad de existencias nunca puede ser negativa.
- Todo lote tiene Código, Descripción, Proveedor, Fecha de vencimiento y Registro sanitario desde la recepción técnica.
- Un lote solo puede estar Disponible, en Cuarentena, Vencido o Bloqueado.
- El código del lote es único.
- No se recibe un lote vencido o que vence hoy (la fecha de vencimiento debe ser posterior a la recepción).

## Componentes y funciones (V5)
- Componente: **Gestión de medicamentos**
- Componente: **Gestión de lotes de medicamentos**
- Función: Control de existencias por lote → `POST /funciones/control-de-existencias-por-lote` (pendiente)
- Función: Gestión del estado del lote → `POST /funciones/gestion-del-estado-del-lote` (pendiente)
- Función: Registros de movimientos del inventario → `POST /funciones/registros-de-movimientos-del-inventario` (pendiente)

## Relaciones con otros contextos (V8)
- Consume a **Seguridad y Auditoría** — «Open Host Service»
- Le sirve a **Abastecimiento** — «Customer / Supplier»
- Le sirve a **Planificación de Demanda** — «Customer / Supplier»
- Le sirve a **Vencimientos** — «Shared Kernel (núcleo compartido: Lote)»
- INT-02 **Historia Clínica (HCE)** (entrada) a través de ACL-01 — intercambia «OBJ-02 — Prescripción médica»
- INT-03 **Servicio de Urgencias** (entrada) a través de ACL-01 — intercambia «OBJ-03 — Necesidad asistencial no programada»
- INT-05 **Proveedores Externos** (entrada) a través de ACL-01 — intercambia «OBJ-05 — Datos de entrega y lote»

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | estado del servicio |
| GET | `/eventos` | eventos de dominio publicados |
| GET | `/arquitectura` | componentes, funciones y caché |
| GET | `/lote-medicamento` | lista de LoteMedicamento |
| GET | `/lote-medicamento/{id}` | un LoteMedicamento |
| POST | `/lote-medicamento/registrar-ingreso` | comando «Registrar Ingreso» → evento «Lote Ingresado» |
| POST | `/lote-medicamento/{id}/descontar-existencias` | comando «Descontar Existencias» → evento «Existencias Descontadas» |
| POST | `/lote-medicamento/{id}/deshacer` | deshace el último comando (memento) |
| POST | `/funciones/control-de-existencias-por-lote` | función «Control de existencias por lote» (pendiente, 501) |
| POST | `/funciones/gestion-del-estado-del-lote` | función «Gestión del estado del lote» (pendiente, 501) |
| POST | `/funciones/registros-de-movimientos-del-inventario` | función «Registros de movimientos del inventario» (pendiente, 501) |

## Ejecutar
```bash
python main.py
```
Por defecto guarda en memoria. Con base de datos real: `PERSISTENCIA=bd` y `BD_URL` (formato del driver:
`postgresql://farmacia:farmacia@localhost:5432/inventario`). La tabla se crea sola al arrancar.

Variables de entorno: `PUERTO`, `PERSISTENCIA` (`memoria` | `bd`), `BD_URL`, `CLAVE_CIFRADO`, `CORS_ORIGENES`, `SEGURIDAD_Y_AUDITORIA_URL`, `ACL_URL`.
