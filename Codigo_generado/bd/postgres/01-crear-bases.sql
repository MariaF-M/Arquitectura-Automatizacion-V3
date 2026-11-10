-- Se ejecuta una sola vez, la primera vez que arranca el contenedor de PostgreSQL.
-- Una base de datos por contexto delimitado (database-per-service). Las tablas las crea cada servicio al arrancar.
CREATE DATABASE inventario;   -- Inventario (D-01)
CREATE DATABASE abastecimiento;   -- Abastecimiento (D-04)
CREATE DATABASE seguridad_y_auditoria;   -- Seguridad y Auditoría (D-05)
