# Planificación de Demanda

> Generado automáticamente desde el modelo ArchiMate. **No editar a mano lo que se pueda regenerar**: cambie el modelo o `spec.yaml` y vuelva a ejecutar el generador.

| | |
|---|---|
| Dominio (V5) | D-03 — Planificación y predicción de demanda |
| Clasificación | SUPPORTING |
| Lenguaje | Python 3.12 |
| Arquitectura | microservicios |
| Puerto | 8003 |
| Base de datos | NoSQL — mongodb |
| Caché | TTL 300 s |
| Campos cifrados | observaciones |

**¿Por qué NoSQL?** Las estimaciones combinan series históricas y agendas con estructura variable según el modelo de predicción; se guardan como documentos versionados y se leen completos para análisis.

## Agregados (V6)

### EstimacionDemanda
Atributos: `medicamento` (texto), `periodo` (texto), `demanda_programada` (entero), `demanda_no_programada` (entero), `cantidad_estimada` (entero), `estado` (texto), `observaciones` (texto)

| Comando | Evento que emite | Regla |
|---|---|---|
| Calcular Demanda | Demanda Estimada | crea el agregado |
| Ajustar Predicción | Predicción Ajustada |  estado → Ajustada; requiere observaciones |

Invariantes:
- La estimación considera demanda programada (cirugías, censo) y no programada (histórico de urgencias).
- Toda predicción es una sugerencia que un humano debe validar antes de pasar a abastecimiento.

## Componentes y funciones (V5)
- Componente: **Gestión de consumo histórico**
- Componente: **Gestión de programación hospitalaria**
- Componente: **Cálculo de necesidad estimada de medicamentos**
- Función: Predicción de demanda → `POST /funciones/prediccion-de-demanda` (pendiente)

## Relaciones con otros contextos (V8)
- Consume a **Inventario** — «Customer / Supplier»
- Le sirve a **Abastecimiento** — «Customer / Supplier»
- INT-01 **Programación Quirúrgica** (entrada) a través de ACL-01 — intercambia «OBJ-01 — Agenda quirúrgica confirmada»

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | estado del servicio |
| GET | `/eventos` | eventos de dominio publicados |
| GET | `/arquitectura` | componentes, funciones y caché |
| GET | `/estimacion-demanda` | lista de EstimacionDemanda |
| GET | `/estimacion-demanda/{id}` | un EstimacionDemanda |
| POST | `/estimacion-demanda/calcular-demanda` | comando «Calcular Demanda» → evento «Demanda Estimada» |
| POST | `/estimacion-demanda/{id}/ajustar-prediccion` | comando «Ajustar Predicción» → evento «Predicción Ajustada» |
| POST | `/estimacion-demanda/{id}/deshacer` | deshace el último comando (memento) |
| POST | `/funciones/prediccion-de-demanda` | función «Predicción de demanda» (pendiente, 501) |

## Ejecutar
```bash
python main.py
```
Por defecto guarda en memoria. Con base de datos real: `PERSISTENCIA=bd` y `BD_URL` (formato del driver:
`mongodb://localhost:27017/planificacion_de_demanda`). La colección se crea sola al arrancar.

Variables de entorno: `PUERTO`, `PERSISTENCIA` (`memoria` | `bd`), `BD_URL`, `CLAVE_CIFRADO`, `CORS_ORIGENES`, `INVENTARIO_URL`, `ACL_URL`.
