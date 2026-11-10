package co.edu.farmacia.anticorrupcion.dominio.traductores;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * INT-06 Entidad de vigilancia farmacéutica (entrada).
 * INVIMA (Vigilancia) --«OBJ-06 — Alerta regulatoria o retiro de lote»--> ACL-01 --comando «Bloquear Lote Vencido»--> Vencimientos
 */
public class TraductorInt06EntidadDeVigilanciaFarmaceutica implements Traductor {
    private static final Map<String, String> MAPEO = new LinkedHashMap<>();
    static {
        MAPEO.put("id_alerta", "id");
        MAPEO.put("motivo_retiro", "motivo");
    }
    /** Variable de entorno con la URL del contexto destino. */
    public static final String VARIABLE_URL = "VENCIMIENTOS_URL";
    public static final String URL_DEFECTO = "http://localhost:8002";
    /** Ruta del comando en el contexto destino ({id} se toma del campo traducido "id"). */
    public static final String RUTA_COMANDO = "/alerta-vencimiento/{id}/bloquear-lote-vencido";

    @Override public String codigo() { return "INT-06"; }
    @Override public String nombre() { return "Entidad de vigilancia farmacéutica"; }
    @Override public String direccion() { return "entrada"; }
    @Override public String contexto() { return "Vencimientos"; }
    @Override public String externo() { return "INVIMA (Vigilancia)"; }
    @Override public Map<String, String> mapeo() { return MAPEO; }
}
