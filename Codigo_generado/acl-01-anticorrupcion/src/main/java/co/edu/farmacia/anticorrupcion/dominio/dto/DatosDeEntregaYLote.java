package co.edu.farmacia.anticorrupcion.dominio.dto;

import java.util.List;
import java.util.Map;

/**
 * «OBJ-05 — Datos de entrega y lote» (Business Object de V9) en el formato de Proveedores Externos.
 * Integración INT-05 Proveedor de medicamentos — entrada.
 */
public record DatosDeEntregaYLote(Map<String, Object> datos) {
    public static final List<String> CAMPOS = List.of("numero_lote", "nombre_comercial", "nit_proveedor", "vence", "registro_invima", "unidades");
}
