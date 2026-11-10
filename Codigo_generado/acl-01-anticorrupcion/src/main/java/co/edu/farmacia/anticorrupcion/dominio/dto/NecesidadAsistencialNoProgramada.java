package co.edu.farmacia.anticorrupcion.dominio.dto;

import java.util.List;
import java.util.Map;

/**
 * «OBJ-03 — Necesidad asistencial no programada» (Business Object de V9) en el formato de Servicio de Urgencias.
 * Integración INT-03 Servicio de urgencias — entrada.
 */
public record NecesidadAsistencialNoProgramada(Map<String, Object> datos) {
    public static final List<String> CAMPOS = List.of("id_lote", "unidades_despachadas");
}
