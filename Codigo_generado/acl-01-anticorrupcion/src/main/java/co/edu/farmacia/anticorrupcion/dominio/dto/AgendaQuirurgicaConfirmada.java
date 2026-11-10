package co.edu.farmacia.anticorrupcion.dominio.dto;

import java.util.List;
import java.util.Map;

/**
 * «OBJ-01 — Agenda quirúrgica confirmada» (Business Object de V9) en el formato de Programación Quirúrgica.
 * Integración INT-01 Programación quirúrgica — entrada.
 */
public record AgendaQuirurgicaConfirmada(Map<String, Object> datos) {
    public static final List<String> CAMPOS = List.of("medicamento_requerido", "fecha_programada", "unidades_por_procedimiento");
}
