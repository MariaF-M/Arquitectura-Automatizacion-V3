-- Esquema postgresql del contexto Inventario (D-01).
-- Generado desde los agregados de V6 + atributos e invariantes de spec.yaml. Una base de datos por contexto.
-- El adaptador de persistencia ejecuta este mismo CREATE TABLE al arrancar, así que este archivo es de referencia.

-- Agregado raíz «LoteMedicamento»
CREATE TABLE IF NOT EXISTS lote_medicamento (
    id VARCHAR(36) PRIMARY KEY,
    codigo VARCHAR(255) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NOT NULL,
    proveedor TEXT NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    registro_sanitario VARCHAR(255) NOT NULL,
    cantidad INTEGER CHECK (cantidad >= 0),
    estado VARCHAR(255) CHECK (estado IN ('Disponible', 'Cuarentena', 'Vencido', 'Bloqueado'))
);
COMMENT ON COLUMN lote_medicamento.proveedor IS 'Cifrado en reposo por la aplicación';
