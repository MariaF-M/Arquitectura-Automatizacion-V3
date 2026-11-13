# Guía completa del proyecto V3 — Farmacia Hospitalaria

*Actualizada el 13 de noviembre de 2026: incluye las correcciones de Salomé y el control de errores.*

Esta guía explica **todo**: qué es el sistema, en qué carpeta está cada cosa, cuáles son los contextos, cómo se
conectan, cómo está hecho cada microservicio por dentro y cómo se ejecuta y demuestra.

---

## 1. La idea en 30 segundos

La opción V3 tiene tres partes, y las tres están en el repositorio:

| Parte | Qué es | Dónde |
|---|---|---|
| **Automatización (V2)** | Un programa que lee el diagrama ArchiMate y **genera todo el código** | `Automatizacion/` |
| **Capas externas (V1)** | Bases de datos SQL y NoSQL, caché, memento, cifrado y despliegue con Docker | Dentro de cada servicio en `Codigo_generado/` |
| **Microfrontends** | Una aplicación web hecha de 7 piezas independientes | `Codigo_generado/frontend/` |

```
Modelo ArchiMate  +  spec.yaml  ──►  generar.py  ──►  Codigo_generado/  ──►  docker compose up  ──►  http://localhost:5100
 (qué existe)       (cómo implementarlo)   (el generador)    (todo el sistema)
```

**Regla de oro:** nada de `Codigo_generado/` se edita a mano. Si algo cambia, se cambia el modelo, el `spec.yaml` o
una plantilla, y se vuelve a ejecutar `generar.py`. Así lo hizo Salomé en su último commit: corrigió las
plantillas y regeneró.

---

## 2. Mapa de carpetas del repositorio

```
Arquitectura-Automatizacion-V3/
├── Modelo_archimate/
│   └── Modelo_Farmacia_mejorado.archimate   ← el diagrama (se abre con Archi)
├── Automatizacion/                          ← EL GENERADOR
│   ├── generar.py                              el que se ejecuta
│   ├── spec.yaml                               lo que el diagrama no dice (lenguajes, BD, atributos, reglas)
│   ├── archimate/                              lee e interpreta el diagrama
│   ├── generadores/                            escribe el código (Python, Java, C#, frontend, despliegue)
│   ├── plantillas/                             los "moldes" del código
│   └── pruebas/                                16 pruebas automáticas
├── Codigo_generado/                         ← TODO EL SISTEMA (lo produce el generador)
│   ├── inventario/                             microservicio Python
│   ├── vencimientos/                           microservicio Java
│   ├── planificacion-de-demanda/               microservicio Python
│   ├── abastecimiento/                         microservicio C#
│   ├── seguridad-y-auditoria/                  microservicio Python
│   ├── acl-01-anticorrupcion/                  capa anticorrupción (Java)
│   ├── frontend/                               shell + 6 microfrontends (React)
│   ├── gateway/nginx.conf                      la URL única del backend
│   ├── bd/postgres/                            creación de las bases SQL
│   ├── contratos/                              contratos OpenAPI y Shared Kernel
│   ├── docker-compose.yml                      levanta TODO
│   ├── TRAZABILIDAD.md                         cada elemento del diagrama → sus archivos
│   └── modelo_intermedio.json                  lo que el generador entendió del diagrama
├── docs/GUIA_DE_REVISION.md                 guía de estudio y preguntas de sustentación
└── README.md                                documento principal (incluye la investigación de microfrontends)
```

---

## 3. Los contextos delimitados

Salen de la vista **V8** del diagrama. Su clasificación sale de **V5**, y sus agregados, comandos y eventos de **V6**.

| Contexto | Dominio | Clasificación | Lenguaje | Arquitectura | Base de datos | Puerto | Carpeta |
|---|---|---|---|---|---|---|---|
| **Inventario** | D-01 | CORE | Python | Hexagonal | PostgreSQL | 8001 | `inventario/` |
| **Vencimientos** | D-02 | CORE | Java | Microservicio (Clean) | MongoDB | 8002 | `vencimientos/` |
| **Planificación de Demanda** | D-03 | SUPPORTING | Python | Microservicio (Clean) | MongoDB | 8003 | `planificacion-de-demanda/` |
| **Abastecimiento** | D-04 | SUPPORTING | C# | Hexagonal | PostgreSQL | 8004 | `abastecimiento/` |
| **Seguridad y Auditoría** | D-05 | GENERIC | Python | Microservicio (Clean) | PostgreSQL | 8005 | `seguridad-y-auditoria/` |
| ACL-01 Anticorrupción | — | — | Java | Hexagonal | — | 8010 | `acl-01-anticorrupcion/` |

### Qué hace cada uno (agregado, comandos y eventos de V6)

| Contexto | Agregado | Comandos → evento que emiten | Regla principal |
|---|---|---|---|
| Inventario | `LoteMedicamento` | Registrar Ingreso → *Lote Ingresado* · Descontar Existencias → *Existencias Descontadas* | Las existencias nunca son negativas; no se recibe un lote vencido |
| Vencimientos | `AlertaVencimiento` | Evaluar Prioridad FEFO → *Prioridad FEFO Calculada* · Bloquear Lote Vencido → *Lote Bloqueado* | FEFO: primero sale lo que vence primero; bloquear solo desde *Activa* |
| Planificación | `EstimacionDemanda` | Calcular Demanda → *Demanda Estimada* · Ajustar Predicción → *Predicción Ajustada* | Ajustar exige observaciones |
| Abastecimiento | `RequerimientoCompra` | Generar Requisición → *Requisición Sugerida* · Autorizar Requisición → *Requerimiento Autorizado* | Nada va al ERP sin autorización del químico farmacéutico |
| Seguridad | (sin agregados en V6) | Solo componentes y funciones | Es el dominio genérico |

### Cómo se relacionan (las flechas de V8)

| Quién consume | A quién | Patrón DDD |
|---|---|---|
| Vencimientos | Inventario | **Shared Kernel** (comparten el concepto *Lote*) |
| Planificación | Inventario | **Customer / Supplier** |
| Abastecimiento | Inventario y Planificación | **Customer / Supplier** |
| Inventario, Vencimientos, Abastecimiento | Seguridad y Auditoría | **Open Host Service** |

### Las integraciones con sistemas externos (V9, todas pasan por la ACL)

| Código | Sistema externo | Contexto | Dirección | Qué dispara |
|---|---|---|---|---|
| INT-01 | Programación Quirúrgica | Planificación | entrada | Calcular Demanda |
| INT-02 | Historia Clínica (HCE) | Inventario | entrada | Descontar Existencias |
| INT-03 | Servicio de Urgencias | Inventario | entrada | Descontar Existencias |
| INT-04 | ERP de Compras | Abastecimiento | **salida** | se envía cuando ocurre *Requerimiento Autorizado* |
| INT-05 | Proveedores | Inventario | entrada | Registrar Ingreso |
| INT-06 | INVIMA | Vencimientos | entrada | Bloquear Lote Vencido |

---

## 4. Cómo se conecta todo

```
NAVEGADOR
  Shell (:5100) ── carga ──► microfrontend del contexto (:5101 … :5106)
                                   │  fetch HTTP
                                   ▼
                           Gateway nginx (:8080)   /api/<contexto>/...
                                   │
        ┌─────────────┬────────────┼──────────────┬──────────────┬───────────────┐
        ▼             ▼            ▼              ▼              ▼               ▼
   inventario   vencimientos  planificacion  abastecimiento  seguridad      acl-01
     :8001         :8002         :8003          :8004          :8005         :8010
        │             │            │              │              │               │
   PostgreSQL     MongoDB      MongoDB        PostgreSQL     PostgreSQL     sistemas
                                                                            externos
```

**Las conexiones, una por una:**

1. **Navegador → Shell:** se abre `http://localhost:5100`.
2. **Shell → microfrontend:** al hacer clic en el menú, el shell descarga ese microfrontend desde su puerto
   (`remoteEntry.js`) usando Module Federation.
3. **Microfrontend → backend:** cada microfrontend llama **solo a su servicio**, siempre a través del gateway:
   `http://localhost:8080/api/inventario/...`.
4. **Gateway → servicio:** nginx reenvía según el prefijo (`/api/inventario/` → `inventario:8001`). El archivo está
   en `Codigo_generado/gateway/nginx.conf`.
5. **Servicio → base de datos:** cada servicio tiene su propia base y crea sus tablas al arrancar.
6. **Sistema externo → ACL → servicio:** el externo manda su formato a la ACL
   (`POST /entrantes/int-05`), la ACL traduce los campos y ejecuta el comando en el servicio interno.
7. **Servicio → ACL → sistema externo:** cuando Abastecimiento emite *Requerimiento Autorizado*, envía los datos a
   la ACL (`/salientes/int-04`), que los traduce al formato del ERP.

**¿Dónde se configura cada conexión?** En `Codigo_generado/docker-compose.yml`, con variables de entorno:
`BD_URL` (a qué base se conecta), `ACL_URL` (dónde está la ACL), `INVENTARIO_URL` y similares (a qué servicio
consume) y `VITE_API_URL` (la dirección del gateway para el frontend).

---

## 5. Cómo está hecho un microservicio por dentro

Hay dos estilos, tal como los define el profesor en la diapositiva *Hexagonal vs Clean*.

### 5.1 Hexagonal (Inventario, Abastecimiento): organizado por lado

```
inventario/
├── dominio/                 ← el núcleo: NO conoce bases de datos ni HTTP
│   ├── modelo/                 lote_medicamento.py (agregado + invariantes + memento), entidades.py, errores.py
│   ├── eventos/                eventos.py (LoteIngresado…), bus_eventos.py
│   ├── memento/                memento.py (Caretaker: historial para deshacer)
│   └── servicios/              servicios.py (componentes y funciones de V5)
├── puertos/
│   ├── entrada/                comandos.py ← lo que la aplicación OFRECE (comandos y sus manejadores)
│   └── salida/                 repositorios.py, clientes.py ← lo que la aplicación NECESITA (interfaces)
├── adaptadores/
│   ├── entrada/                http.py ← API REST (recibe peticiones y llama a los comandos)
│   └── salida/
│       ├── persistencia/       memoria.py, base_datos.py (PostgreSQL), cache.py
│       ├── clientes/           http.py (llamadas a otros servicios y a la ACL)
│       └── transversal/        cifrado.py
├── contratos/               eventos_v1.py ← lenguaje publicado (LoteIngresadoV1…)
├── shared_kernel/           Lote compartido con Vencimientos
├── db/esquema.sql           esquema de referencia
└── main.py                  raíz de composición: aquí se conectan puertos con adaptadores
```

En C# (Abastecimiento) es lo mismo con mayúsculas: `Dominio/`, `Puertos/Entrada`, `Puertos/Salida`,
`Adaptadores/Entrada`, `Adaptadores/Salida/...`, `Contratos/` y `Program.cs`.

### 5.2 Microservicio con Clean Architecture (Vencimientos, Planificación, Seguridad): organizado por capa

```
planificacion-de-demanda/
├── api/                     http.py ← controladores (entrada HTTP)
├── aplicacion/              comandos/, servicios/, memento/, eventos/ ← casos de uso
├── dominio/                 modelo/, eventos/, puertos/ ← reglas de negocio e interfaces
├── infraestructura/         persistencia/ (MongoDB, caché), clientes/, transversal/ (cifrado)
├── contratos/               eventos_v1.py
└── main.py
```

En Java (Vencimientos) las mismas capas están en `src/main/java/co/edu/farmacia/vencimientos/`:
`api/`, `aplicacion/`, `dominio/`, `infraestructura/`, `contratos/`, `sharedkernel/` y `Main.java`.

**La regla en los dos estilos:** las dependencias apuntan hacia adentro. El dominio nunca importa adaptadores ni
infraestructura, y hay una prueba automática que lo verifica.

### 5.3 Recorrido de un comando (de punta a punta)

Ejemplo: "Descontar 30 unidades del lote X" en Inventario.

1. **`adaptadores/entrada/http.py`** recibe `POST /lote-medicamento/X/descontar-existencias {"cantidad": 30}` y crea el
   comando `DescontarExistencias`.
2. **`puertos/entrada/comandos.py`** (manejador):
   1. Carga el lote por el puerto `RepositorioLoteMedicamento`.
   2. Toma un **memento** (foto del estado actual).
   3. Le pide al agregado que ejecute el comando.
3. **`dominio/modelo/lote_medicamento.py`** resta la cantidad y llama a `validar()`. Si quedara negativo, lanza
   `ReglaNegocioError`.
4. Según el resultado:
   - **Si falló:** el manejador restaura el memento (no queda nada a medias) y la API responde **422** con el
     mensaje.
   - **Si salió bien:** guarda el memento en el `Caretaker` (para "Deshacer"), guarda el lote por el repositorio
     (pasando por la caché y el cifrado) y publica el evento *Existencias Descontadas*, traducido a su contrato V1.
     La API responde **201** con el lote actualizado.

### 5.4 Las rutas de la API (iguales en todos los servicios)

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/salud` | ¿Está vivo? |
| GET | `/<agregado>` | Lista los registros |
| GET | `/<agregado>/{id}` | Uno por id |
| POST | `/<agregado>/<comando-que-crea>` | Crea, por ejemplo `/lote-medicamento/registrar-ingreso` |
| POST | `/<agregado>/{id}/<comando>` | Ejecuta un comando sobre uno existente |
| POST | `/<agregado>/{id}/deshacer` | Deshace el último cambio (memento) |
| GET | `/eventos` | Eventos publicados (con su contrato V1); útil para revisar con `curl` |
| GET | `/arquitectura` | Componentes, funciones y estadísticas de la caché |
| POST | `/funciones/<funcion>` | Funciones de V5 (responden 501: pendientes) |

---

## 6. Bases de datos, caché, memento, cifrado, eventos y contratos

| Elemento | Dónde está | Cómo funciona |
|---|---|---|
| **PostgreSQL** | Contenedor `postgres` | Bases `inventario`, `abastecimiento` y `seguridad_y_auditoria`, creadas por el servicio `bd-init` del compose. Cada servicio crea sus tablas al arrancar. |
| **MongoDB** | Contenedor `mongo` | Bases `vencimientos` y `planificacion_de_demanda`. Un documento por agregado. |
| **Memoria vs BD** | Variable `PERSISTENCIA` | `memoria` para desarrollo, `bd` en Docker. Mismo puerto, dos adaptadores. |
| **Caché** | `.../persistencia/cache.py` | Decorador del repositorio con expiración (TTL); se invalida al escribir. El TTL de cada contexto está en `spec.yaml`. |
| **Memento** | Agregado + `Caretaker` | Revierte si un comando viola una regla y permite "Deshacer". |
| **Cifrado** | `.../transversal/cifrado.py` | Los campos sensibles se guardan como `enc:...` en la base. Cuáles se cifran se define en `spec.yaml`. |
| **Eventos** | `bus_eventos.py` | Bus en memoria (Observer). Por ejemplo, *Requerimiento Autorizado* dispara el envío al ERP. |
| **Contratos V1** | `contratos/` | Lenguaje publicado: `LoteIngresadoV1`…, solo con tipos primitivos y sin depender del dominio. |

**Ver los datos** (con Docker corriendo, desde `Codigo_generado`):

```bash
docker compose exec postgres psql -U farmacia -d inventario -c "select * from lote_medicamento;"
docker compose exec mongo mongosh vencimientos --eval "db.alerta_vencimiento.find()"
```

O con DBeaver o pgAdmin (`localhost:5432`, usuario y clave `farmacia`) y con MongoDB Compass (`mongodb://localhost:27017`).

---

## 7. Microfrontends

**Tecnología:** TypeScript + React + Vite + Module Federation 2.0 (plugin oficial `@module-federation/vite`).

| App | Puerto | Carpeta |
|---|---|---|
| Shell (contenedor) | 5100 | `frontend/shell/` |
| Inventario | 5101 | `frontend/mf-inventario/` |
| Vencimientos | 5102 | `frontend/mf-vencimientos/` |
| Planificación | 5103 | `frontend/mf-planificacion-de-demanda/` |
| Abastecimiento | 5104 | `frontend/mf-abastecimiento/` |
| Seguridad | 5105 | `frontend/mf-seguridad-y-auditoria/` |
| Integraciones (simulador de la ACL) | 5106 | `frontend/mf-integraciones/` |

**Los tres mecanismos:**

| Mecanismo | Quién inicia | Archivo | Para qué |
|---|---|---|---|
| Carga con `import('mf_x/App')` | El shell, al elegir en el menú | `shell/vite.config.ts`, `shell/src/remotos.ts`, `shell/src/App.tsx` | Descargar y mostrar el microfrontend |
| `fetch()` HTTP | El microfrontend | `mf-*/src/api.ts` | Consultar y ejecutar comandos en **su** servicio, vía gateway |
| `CustomEvent('farmacia:evento')` | El microfrontend, cuando un comando sale bien | `mf-*/src/eventos.ts` → lo escucha `shell/src/App.tsx` | Avisar; el shell lo muestra en "Actividad" |

Los microfrontends **no se llaman entre sí ni comparten estado**. Si necesitan datos, los piden al backend.

Cada pantalla de contexto muestra solo lo útil para el usuario: el encabezado (dominio, clasificación, tecnología),
sus relaciones y un panel por agregado con su formulario, tabla, comandos y "Deshacer". Las funciones de V5 (aún sin
lógica) y el listado técnico de eventos no se muestran; los eventos se ven en el panel **"Actividad"** del shell.

**Generados del diagrama:** cada microfrontend tiene un `src/contexto.json` con sus agregados, comandos, atributos y
reglas. El código React (`src/componentes/`) es genérico y arma formularios, tablas y botones a partir de ese archivo.

---

## 8. El generador y cómo trabajar con él

### Las piezas (`Automatizacion/`)

| Archivo | Rol |
|---|---|
| `generar.py` | Orquesta todo: lee, valida, genera e imprime el resumen |
| `spec.yaml` | Lenguaje, arquitectura, BD (con justificación), atributos, invariantes, efecto de cada comando, caché, cifrado e integraciones |
| `archimate/lector.py` | Lee el XML del `.archimate` |
| `archimate/extractor.py` | Interpreta V5, V6, V8 y V9 con reglas DDD y valida contra el spec (**el archivo más importante**) |
| `archimate/modelo.py` | El modelo intermedio (Contexto, Agregado, Comando…) |
| `generadores/*.py` | Un generador por lenguaje, más el del frontend y el de despliegue (`comun.py`) |
| `plantillas/` | Los moldes Jinja2 (`.j2`) que se rellenan con los datos del diagrama |
| `pruebas/test_generador.py` | 16 pruebas |

### Cómo hacer un cambio (flujo de trabajo del equipo)

| Si quiero… | Cambio… |
|---|---|
| Agregar o renombrar un comando, evento o agregado | El **diagrama** en Archi (V6) |
| Cambiar el lenguaje, la arquitectura o la BD de un contexto | `spec.yaml` |
| Agregar un atributo o una regla (por ejemplo, "no negativo") | `spec.yaml` |
| Cambiar cómo se ve o funciona el código de todos los servicios | Una **plantilla** en `Automatizacion/plantillas/` |

Y después siempre:

```bash
pip install -r Automatizacion/requirements.txt     # solo la primera vez
python3 Automatizacion/generar.py --validar         # revisa sin escribir
python3 Automatizacion/generar.py                   # regenera Codigo_generado/
python3 -m unittest discover -s Automatizacion/pruebas -v
```

Luego `git add -A`, `git commit` y `git push`. **Nunca se edita `Codigo_generado/` a mano**, porque se borra en
cada regeneración.

---

## 9. Ejecutar, verificar y demostrar

### Levantar todo

```bash
cd Codigo_generado
docker compose up --build        # la primera vez tarda varios minutos
```

| Qué | Dirección |
|---|---|
| Aplicación web | http://localhost:5100 |
| Gateway | http://localhost:8080/api/inventario/salud |
| PostgreSQL / MongoDB | `localhost:5432` / `localhost:27017` |

Para apagar: `docker compose down`, o `docker compose down -v` para borrar también los datos.

### Demostración sugerida (unos 10 minutos)

1. **Inventario:**
   1. Intentar registrar un lote con el código `ABC` (el formulario lo rechaza: solo números). Luego registrarlo bien; probar una fecha pasada y un código repetido, que también se rechazan.
   2. Descontar 30 unidades; intentar descontar 999, que lo rechaza la invariante.
   3. Deshacer (memento).
   4. Mostrar los eventos en "Actividad".
2. **DBeaver:** mostrar la fila en PostgreSQL con el proveedor cifrado (`enc:...`).
3. **Integraciones:** INT-05, el proveedor envía su formato y aparece en Inventario; INT-02, la historia clínica
   descuenta existencias.
4. **Vencimientos (Java + MongoDB):** evaluar FEFO y bloquear; el botón queda deshabilitado.
5. **Abastecimiento (C#):** autorizar sin químico (lo rechaza) y luego con químico. Mostrar en
   `docker compose logs acl-01-anticorrupcion` el envío traducido al ERP.
6. **Resiliencia:** `docker compose stop mf-vencimientos` y mostrar que el resto de la aplicación sigue funcionando.
7. **Automatización:** abrir `TRAZABILIDAD.md`, buscar un comando de V6 y mostrar los archivos que generó.
   Ejecutar `generar.py --validar` con un nombre cambiado en el spec para mostrar que el diagrama manda.

### Cambios recientes en el repositorio (13 de noviembre, Salomé)

- **`bd-init` en el docker-compose:** un contenedor que crea las bases SQL si no existen. Corrige el caso en que el
  volumen de PostgreSQL ya existía y el script inicial no se volvía a ejecutar. Los servicios SQL ahora esperan a
  que termine (`service_completed_successfully`).
- **Healthcheck de PostgreSQL con `-h 127.0.0.1`:** evita que se marque como listo antes de terminar de
  inicializarse.
- **`api.ts` de los microfrontends:** si el gateway responde con una página HTML de error (servicio caído), muestra
  un mensaje claro en vez de romperse.
- **`main.py` de los servicios Python:** importa el adaptador de base de datos solo si `PERSISTENCIA=bd`, así se
  pueden ejecutar en memoria sin instalar `psycopg` ni `pymongo`.

Todo se hizo en las plantillas y se regeneró, como debe ser: 88/88 elementos trazados y las pruebas pasan. El único
detalle es que se subió `frontend/package-lock.json` (sale de `npm install`). No hace daño; desaparece al regenerar.

---

## 10. Control de errores

Cada regla se escribe una sola vez en `spec.yaml` y el generador la valida en **todas las capas**:

1. **Frontend:** antes de enviar, `validar()` (en `mf-*/src/componentes/Campo.tsx`) revisa obligatorios, números,
   rangos, largos, patrones y fechas. Si hay errores, los lista en español y **no llama al backend**.
2. **Dominio** (el agregado, en Python, Java y C#):
   - Convierte y valida los tipos: `"diez"` o `2.5` no son enteros, y una fecha debe ir como `AAAA-MM-DD`.
   - Quita espacios sobrantes, de modo que un texto de solo espacios cuenta como vacío.
   - Aplica los patrones: por ejemplo, el **código de lote solo acepta números** y no puede repetirse.
   - Aplica los rangos, exige que la cantidad a descontar sea **mayor que cero** y revisa los estados permitidos.
   - Aplica los mínimos de cada comando: un lote se registra con **al menos 1 unidad** (luego puede llegar a 0).

   Si algo falla, responde **422** con el mensaje.
3. **API:**
   - JSON roto o cuerpo que no es un objeto: **400**.
   - Ruta inexistente: **404**.
   - Cualquier error inesperado: **500** con un mensaje JSON, sin caerse ni mostrar detalles internos (el detalle
     queda en el log).
4. **Base de datos:** `NOT NULL`, `CHECK` y `UNIQUE` como última barrera.

Ejemplo de regla en `spec.yaml`:

```yaml
formatos:
  codigo: {patron: '^[0-9]{3,20}$', mensaje: 'debe tener solo números, entre 3 y 20 dígitos'}
  cantidad: {maximo: 1000000}
unicos: [codigo]
```

La tabla completa de reglas está en la sección "Control de errores" del README.

---

## Preguntas rápidas de sustentación

- **¿Qué automatizaron?** La lectura del diagrama (V5, V6, V8, V9) y la generación de 5 microservicios en 3
  lenguajes, la ACL, 7 aplicaciones de frontend, bases de datos, gateway y despliegue, con trazabilidad del 100 %.
- **¿Por qué hexagonal en unos y Clean en otros?** Hexagonal donde hay varios externos que aislar (Inventario:
  HCE, urgencias, proveedores; Abastecimiento: ERP). Clean en los demás, como en el ejemplo del profesor.
- **¿Por qué SQL y NoSQL?** SQL donde se necesita consistencia (existencias, requisiciones auditables); NoSQL para
  documentos de estructura variable (alertas, estimaciones).
- **¿Cómo se comunican los microfrontends?** No se llaman entre sí: publican `CustomEvent` y el shell escucha; los
  datos se piden al backend por el gateway.
- **¿Qué falta?** La lógica de las funciones de V5 (el diagrama no trae los algoritmos), la autenticación real y un
  broker de mensajes entre servicios. Todo está documentado como trabajo futuro.
