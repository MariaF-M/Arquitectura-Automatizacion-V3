package co.edu.farmacia.anticorrupcion.dominio.dto;

import java.util.List;
import java.util.Map;

/**
 * «OBJ-04 — Requerimiento y estado de compra» (Business Object de V9) en el formato que espera Sistema ERP (Compras).
 * Integración INT-04 ERP de compras y contabilidad — salida.
 */
public record RequerimientoYEstadoDeCompra(Map<String, Object> datos) {
    public static final List<String> CAMPOS = List.of("dci", "concentracion", "cantidad_solicitada", "prioridad");
}
