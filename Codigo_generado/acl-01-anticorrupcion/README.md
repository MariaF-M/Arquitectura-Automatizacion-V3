# ACL-01 Adaptador anticorrupción e interoperabilidad

> Generado automáticamente desde V9 (Interoperabilidad y anticorrupción) y V8 (relaciones «ACL»).

Interfaz: **IF-ACL-01 - Interfaz de integración** · Lenguaje: Java 17 · Arquitectura: hexagonal · Puerto: 8010

La ACL es el único punto de contacto con sistemas externos. Recibe el formato del externo (DTO),
lo **traduce** al lenguaje ubicuo de la farmacia y lo entrega como un comando del contexto interno;
o al revés, toma un evento interno y lo traduce al formato del externo. Así el modelo de los
sistemas externos no contamina los dominios.

| Código | Integración (V9) | Sistema externo (V8) | Objeto (V9) | Dirección | Contexto | Comando / evento | Mapeo |
|---|---|---|---|---|---|---|---|
| INT-01 | Programación quirúrgica | Programación Quirúrgica | OBJ-01 — Agenda quirúrgica confirmada | entrada | Planificación de Demanda | Calcular Demanda | `medicamento_requerido→medicamento` `fecha_programada→periodo` `unidades_por_procedimiento→demanda_programada`  |
| INT-02 | Historia clínica electrónica | Historia Clínica (HCE) | OBJ-02 — Prescripción médica | entrada | Inventario | Descontar Existencias | `id_lote→id` `unidades_prescritas→cantidad`  |
| INT-03 | Servicio de urgencias | Servicio de Urgencias | OBJ-03 — Necesidad asistencial no programada | entrada | Inventario | Descontar Existencias | `id_lote→id` `unidades_despachadas→cantidad`  |
| INT-04 | ERP de compras y contabilidad | Sistema ERP (Compras) | OBJ-04 — Requerimiento y estado de compra | salida | Abastecimiento | Requerimiento Autorizado | `principio_activo→dci` `concentracion→concentracion` `cantidad→cantidad_solicitada` `nivel_urgencia→prioridad`  |
| INT-05 | Proveedor de medicamentos | Proveedores Externos | OBJ-05 — Datos de entrega y lote | entrada | Inventario | Registrar Ingreso | `numero_lote→codigo` `nombre_comercial→descripcion` `nit_proveedor→proveedor` `vence→fecha_vencimiento` `registro_invima→registro_sanitario` `unidades→cantidad`  |
| INT-06 | Entidad de vigilancia farmacéutica | INVIMA (Vigilancia) | OBJ-06 — Alerta regulatoria o retiro de lote | entrada | Vencimientos | Bloquear Lote Vencido | `id_alerta→id` `motivo_retiro→motivo`  |

## API
| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | estado del servicio |
| GET | `/integraciones` | catálogo de integraciones INT-xx |
| POST | `/entrantes/int-01` | INT-01 Programación quirúrgica: traduce «OBJ-01 — Agenda quirúrgica confirmada» → comando «Calcular Demanda» en Planificación de Demanda |
| POST | `/entrantes/int-02` | INT-02 Historia clínica electrónica: traduce «OBJ-02 — Prescripción médica» → comando «Descontar Existencias» en Inventario |
| POST | `/entrantes/int-03` | INT-03 Servicio de urgencias: traduce «OBJ-03 — Necesidad asistencial no programada» → comando «Descontar Existencias» en Inventario |
| POST | `/salientes/int-04` | INT-04 ERP de compras y contabilidad: traduce «OBJ-04 — Requerimiento y estado de compra» → Sistema ERP (Compras) |
| POST | `/entrantes/int-05` | INT-05 Proveedor de medicamentos: traduce «OBJ-05 — Datos de entrega y lote» → comando «Registrar Ingreso» en Inventario |
| POST | `/entrantes/int-06` | INT-06 Entidad de vigilancia farmacéutica: traduce «OBJ-06 — Alerta regulatoria o retiro de lote» → comando «Bloquear Lote Vencido» en Vencimientos |

## Ejecutar
```bash
mvn -q package && java -jar target/acl-01-anticorrupcion.jar
# o sin Maven:
javac -d out $(find src -name "*.java") && java -cp out co.edu.farmacia.anticorrupcion.Main
```
Variables: `PUERTO`, `INVENTARIO_URL`, `VENCIMIENTOS_URL`, `PLANIFICACION_DE_DEMANDA_URL`, `ABASTECIMIENTO_URL`, y `EXT_INT_0X_URL` para cada sistema externo (si no está, la salida se registra en el log).
