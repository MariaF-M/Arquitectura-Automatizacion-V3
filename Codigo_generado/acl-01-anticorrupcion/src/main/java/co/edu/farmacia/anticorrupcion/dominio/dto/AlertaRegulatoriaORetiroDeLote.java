package co.edu.farmacia.anticorrupcion.dominio.dto;

import java.util.List;
import java.util.Map;

/**
 * «OBJ-06 — Alerta regulatoria o retiro de lote» (Business Object de V9) en el formato de INVIMA (Vigilancia).
 * Integración INT-06 Entidad de vigilancia farmacéutica — entrada.
 */
public record AlertaRegulatoriaORetiroDeLote(Map<String, Object> datos) {
    public static final List<String> CAMPOS = List.of("id_alerta", "motivo_retiro");
}
