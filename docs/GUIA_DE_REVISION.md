# Guía de revisión del proyecto

Esta guía es para que todo el equipo entienda el proyecto a fondo antes de la sustentación. En la
sustentación **cualquiera puede ser preguntado por cualquier parte**, así que la idea es que cada una revise un
bloque a fondo y después se lo explique a las demás.

## 1. La idea en una frase

> El **diagrama ArchiMate** dice qué existe; **`spec.yaml`** dice lo que el diagrama no puede decir (lenguaje,
> base de datos, atributos); **el generador** cruza los dos y escribe todo el sistema; **`TRAZABILIDAD.md`**
> demuestra que cada elemento del diagrama terminó en código.

```
Modelo .archimate ─┐
                   ├─► extractor (reglas DDD + validación) ─► modelo intermedio ─► generadores ─► Codigo_generado/
spec.yaml ─────────┘
```

## 2. Reparto sugerido (3 bloques)

### Bloque A — El generador (la parte de "automatización", el corazón de la V3)
Leer en este orden:
1. `Automatizacion/spec.yaml`: qué se configura y por qué. Comparar con el documento de V6 de la entrega 3.
2. `Automatizacion/archimate/lector.py`: cómo se lee el XML de Archi (elementos, relaciones, vistas y anidamiento).
3. `Automatizacion/archimate/extractor.py`: **el más importante**. Ver los métodos `_dominios` (V5),
   `_agregados_por_dominio` (V6), `_mapa_contextos` (V8) e `_integraciones` (V9), y todos los `ErrorModelo` (validaciones).
4. `Automatizacion/archimate/modelo.py`: el modelo intermedio.
5. `Automatizacion/generadores/base.py` y `python_gen.py`: cómo se escribe un archivo y se registra la trazabilidad.
6. `Automatizacion/generar.py`: el orden de todo.

Ejercicio para entenderlo: en `spec.yaml`, cambie `arquitectura: hexagonal` por `microservicios` en Inventario,
ejecute `python Automatizacion/generar.py` y compare las carpetas de `Codigo_generado/inventario`.

### Bloque B — El backend generado
Recorrer **un** contexto completo. Inventario es el más representativo (`Codigo_generado/inventario/`, hexagonal):
1. `README.md` del servicio: resumen del contexto.
2. `dominio/modelo/lote_medicamento.py`: el agregado, sus invariantes (`validar`) y el memento (`crear_memento`, `restaurar`).
3. `puertos/entrada/comandos.py`: el flujo de un comando (memento → ejecutar → validar → guardar → publicar eventos).
4. `puertos/salida/repositorios.py` → `adaptadores/salida/persistencia/memoria.py`, `base_datos.py` y `cache.py`: un
   puerto y tres adaptadores.
5. `adaptadores/salida/transversal/cifrado.py`: el cifrado.
6. `main.py`: dónde se conecta todo (raíz de composición).

Después, mirar las diferencias en los otros lenguajes:
- `vencimientos/` (Java, en capas).
- `abastecimiento/` (C#, hexagonal).
- `acl-01-anticorrupcion/` (Java): los traductores `Traductor*.java` y `ServicioIntegracion.java`.

### Bloque C — Microfrontends y despliegue
1. Sección 9 del `README.md` principal (la investigación y sus fuentes).
2. `Codigo_generado/frontend/shell/vite.config.ts` y `src/remotos.ts`: cómo el *host* declara y carga los remotos.
3. `Codigo_generado/frontend/mf-inventario/vite.config.ts`: cómo un remoto se expone (`exposes: './App'`).
4. `mf-inventario/src/contexto.json`: **lo que el generador saca del diagrama para la interfaz**.
5. `mf-inventario/src/componentes/PanelAgregado.tsx`: cómo ese JSON se vuelve formularios y botones.
6. `src/eventos.ts` y `shell/src/App.tsx`: comunicación por `CustomEvent`.
7. `shell/src/LimiteErrores.tsx`: aislamiento de fallos.
8. `Codigo_generado/docker-compose.yml` y `gateway/nginx.conf`: el despliegue.

## 3. Cómo seguir un elemento del diagrama hasta el código

Abra `Codigo_generado/TRAZABILIDAD.md` y busque, por ejemplo, **«Descontar Existencias»**. Aparece como
*ApplicationProcess* de V6, y debajo están todos los archivos que generó: el método del agregado, el comando,
la ruta HTTP, el `contexto.json` del microfrontend… Es la mejor forma de responder "¿dónde está X del diagrama?".

## 4. Preguntas probables y cómo responderlas

**¿Qué hace exactamente la automatización?**
Lee el `.archimate` y extrae los contextos (V8), sus dominios y clasificación (V5), sus agregados, comandos y
eventos (V6) y las integraciones (V9). Lo cruza con `spec.yaml` y genera, por cada contexto, un servicio con su base
de datos y un microfrontend, más la capa anticorrupción, el gateway y el docker-compose.

**¿Por qué existe `spec.yaml`? ¿No debería salir todo del diagrama?**
ArchiMate modela estructura y comportamiento, no detalles de implementación: no tiene dónde decir "este contexto
va en Java" ni "este atributo es una fecha". El spec es el equivalente al documento de especificaciones de la
entrega 3. Lo importante es que **no puede inventar nada**: si nombra algo que no está en el diagrama, falla.

**¿Por qué hexagonal en unos contextos y capas en otros?**
Tabla de la sección 6 del README. En resumen: hexagonal donde hay varios sistemas externos que aislar (Inventario
con HCE, urgencias y proveedores; Abastecimiento con el ERP). Capas donde la lógica es acotada o el dominio es de
soporte o genérico.

**¿Por qué SQL en unos y NoSQL en otros?**
Inventario y Abastecimiento necesitan transacciones e integridad: existencias que no pueden quedar negativas y
requerimientos auditables. Vencimientos y Planificación manejan documentos de estructura variable que se leen
completos. Cada contexto tiene su propia base de datos (*database per service*).

**¿Dónde está el memento y para qué sirve?**
En el agregado (`crear_memento` / `restaurar`) y en el `Caretaker`. Sirve para dos cosas: revertir si un comando
viola una invariante, y deshacer el último cambio (`POST /{id}/deshacer`, el botón "Deshacer" del frontend).

**¿Dónde está la caché?**
`RepositorioConCache`, un decorador del repositorio con expiración (TTL) que se invalida al escribir. El dominio no
sabe que existe. Sus aciertos y fallos se ven en `GET /arquitectura`.

**¿Qué se cifra y dónde?**
Los campos marcados en `spec.yaml` (por ejemplo, el proveedor). Se cifran en el adaptador de persistencia, así que
en la base de datos quedan como `enc:...` y el dominio nunca ve el texto cifrado. Es un cifrado didáctico (XOR +
Base64); cambiarlo por AES solo toca la clase `Cifrador`.

**¿Qué es la capa anticorrupción y por qué un servicio aparte?**
Es el único que conoce el formato de los sistemas externos. Por ejemplo, el proveedor manda `numero_lote` y
`unidades`; la ACL lo traduce a `codigo` y `cantidad` y ejecuta el comando «Registrar Ingreso» en Inventario. Así,
si el proveedor cambia su formato, solo cambia el traductor.

**¿Qué es un microfrontend y por qué Module Federation?**
Una parte de la interfaz que se construye y despliega sola y se compone con las demás en el navegador. Elegimos
Module Federation porque integra en tiempo de ejecución, que es lo que recomienda el artículo de Fowler (no en
compilación, que obliga a publicar todo junto). Además comparte React una sola vez y es el estándar actual: la
versión 2.0 es estable y tiene plugin oficial para Vite.

**¿Cómo se comunican los microfrontends entre sí?**
Casi no se comunican, a propósito. Cuando uno ejecuta un comando, publica un `CustomEvent` (`farmacia:evento`) y el
shell lo muestra en "Actividad". No hay estado compartido.

**¿Qué pasa si un microfrontend se cae?**
Solo esa sección muestra un aviso (`LimiteErrores`); el menú y los demás siguen funcionando.

**¿Qué falta? ¿Por qué las funciones responden 501?**
El diagrama dice que existen funciones como «Predicción de demanda», pero no su algoritmo. El generador deja el
punto de extensión listo y lo declara honestamente. Más detalle en la sección 14 del README.

## 5. Antes de la sustentación

- [ ] Ejecutar `docker compose up --build` en `Codigo_generado/` y hacer la demostración de la sección 11 del
      README completa al menos una vez. **Esta es también la primera prueba real del adaptador de BD de C#.**
- [ ] Ejecutar `python -m unittest discover -s Automatizacion/pruebas -v` y saber explicar qué prueba cada test.
- [ ] Hacer el ejercicio de "el diagrama manda" (renombrar un comando en Archi y regenerar).
- [ ] Revisar y ajustar con sus propias palabras las justificaciones de la sección 6 del README.
