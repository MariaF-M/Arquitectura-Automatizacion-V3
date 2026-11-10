-- Esquema postgresql del contexto Abastecimiento (D-04).
-- Generado desde los agregados de V6 + atributos e invariantes de spec.yaml. Una base de datos por contexto.
-- El adaptador de persistencia ejecuta este mismo CREATE TABLE al arrancar, así que este archivo es de referencia.

-- Agregado raíz «RequerimientoCompra»
CREATE TABLE IF NOT EXISTS requerimiento_compra (
    id VARCHAR(36) PRIMARY KEY,
    principio_activo VARCHAR(255) NOT NULL,
    concentracion VARCHAR(255) NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
    nivel_urgencia VARCHAR(255) NOT NULL CHECK (nivel_urgencia IN ('Baja', 'Media', 'Alta', 'Critica')),
    estado VARCHAR(255) CHECK (estado IN ('Sugerido', 'Autorizado')),
    autorizado_por TEXT
);
COMMENT ON COLUMN requerimiento_compra.autorizado_por IS 'Cifrado en reposo por la aplicación';
