package co.edu.farmacia.anticorrupcion.dominio.traductores;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * INT-03 Servicio de urgencias (entrada).
 * Servicio de Urgencias --«OBJ-03 — Necesidad asistencial no programada»--> ACL-01 --comando «Descontar Existencias»--> Inventario
 */
public class TraductorInt03ServicioDeUrgencias implements Traductor {
    private static final Map<String, String> MAPEO = new LinkedHashMap<>();
    static {
        MAPEO.put("id_lote", "id");
        MAPEO.put("unidades_despachadas", "cantidad");
    }
    /** Variable de entorno con la URL del contexto destino. */
    public static final String VARIABLE_URL = "INVENTARIO_URL";
    public static final String URL_DEFECTO = "http://localhost:8001";
    /** Ruta del comando en el contexto destino ({id} se toma del campo traducido "id"). */
    public static final String RUTA_COMANDO = "/lote-medicamento/{id}/descontar-existencias";

    @Override public String codigo() { return "INT-03"; }
    @Override public String nombre() { return "Servicio de urgencias"; }
    @Override public String direccion() { return "entrada"; }
    @Override public String contexto() { return "Inventario"; }
    @Override public String externo() { return "Servicio de Urgencias"; }
    @Override public Map<String, String> mapeo() { return MAPEO; }
}
