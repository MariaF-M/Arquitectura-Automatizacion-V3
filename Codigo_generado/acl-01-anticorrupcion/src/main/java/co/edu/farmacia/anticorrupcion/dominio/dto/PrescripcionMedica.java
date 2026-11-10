package co.edu.farmacia.anticorrupcion.dominio.dto;

import java.util.List;
import java.util.Map;

/**
 * «OBJ-02 — Prescripción médica» (Business Object de V9) en el formato de Historia Clínica (HCE).
 * Integración INT-02 Historia clínica electrónica — entrada.
 */
public record PrescripcionMedica(Map<String, Object> datos) {
    public static final List<String> CAMPOS = List.of("id_lote", "unidades_prescritas");
}
