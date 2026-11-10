# Código generado — farmacia-hospitalaria

> Todo lo que hay en esta carpeta lo produjo `Automatizacion/generar.py` a partir de
> `Modelo_archimate/Modelo_Farmacia_mejorado.archimate` + `Automatizacion/spec.yaml`. Para cambiarlo, cambie el
> modelo o el spec y regenere.

| Servicio | Dominio | Clasif. | Lenguaje | Arquitectura | Puerto | BD |
|---|---|---|---|---|---|---|
| [Inventario](inventario/README.md) | D-01 | CORE | python | hexagonal | 8001 | postgresql |
| [Vencimientos](vencimientos/README.md) | D-02 | CORE | java | microservicios | 8002 | mongodb |
| [Planificación de Demanda](planificacion-de-demanda/README.md) | D-03 | SUPPORTING | python | microservicios | 8003 | mongodb |
| [Abastecimiento](abastecimiento/README.md) | D-04 | SUPPORTING | csharp | hexagonal | 8004 | postgresql |
| [Seguridad y Auditoría](seguridad-y-auditoria/README.md) | D-05 | GENERIC | python | microservicios | 8005 | postgresql |
| [ACL-01 Anticorrupción](acl-01-anticorrupcion/README.md) | — | — | java | hexagonal | 8010 | — |

- `frontend/`: shell + microfrontends (React + TypeScript + Module Federation). Ver `frontend/README.md`.
- `gateway/nginx.conf`: una sola URL para todo el backend (`http://localhost:8080/api/<contexto>`).
- `bd/postgres/`: creación de una base de datos por contexto SQL.
- `contratos/`: contrato OpenAPI de cada servicio y el Shared Kernel en JSON Schema.
- `docker-compose.yml`: despliegue de todo (`docker compose up --build`, luego abrir http://localhost:5100).
- `TRAZABILIDAD.md`: cada elemento del diagrama y los archivos que generó.
- `modelo_intermedio.json`: lo que el generador entendió del modelo.
