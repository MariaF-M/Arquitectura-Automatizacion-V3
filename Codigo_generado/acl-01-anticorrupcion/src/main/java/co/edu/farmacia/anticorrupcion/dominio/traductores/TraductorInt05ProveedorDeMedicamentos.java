package co.edu.farmacia.anticorrupcion.dominio.traductores;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * INT-05 Proveedor de medicamentos (entrada).
 * Proveedores Externos --«OBJ-05 — Datos de entrega y lote»--> ACL-01 --comando «Registrar Ingreso»--> Inventario
 */
public class TraductorInt05ProveedorDeMedicamentos implements Traductor {
    private static final Map<String, String> MAPEO = new LinkedHashMap<>();
    static {
        MAPEO.put("numero_lote", "codigo");
        MAPEO.put("nombre_comercial", "descripcion");
        MAPEO.put("nit_proveedor", "proveedor");
        MAPEO.put("vence", "fecha_vencimiento");
        MAPEO.put("registro_invima", "registro_sanitario");
        MAPEO.put("unidades", "cantidad");
    }
    /** Variable de entorno con la URL del contexto destino. */
    public static final String VARIABLE_URL = "INVENTARIO_URL";
    public static final String URL_DEFECTO = "http://localhost:8001";
    /** Ruta del comando en el contexto destino ({id} se toma del campo traducido "id"). */
    public static final String RUTA_COMANDO = "/lote-medicamento/registrar-ingreso";

    @Override public String codigo() { return "INT-05"; }
    @Override public String nombre() { return "Proveedor de medicamentos"; }
    @Override public String direccion() { return "entrada"; }
    @Override public String contexto() { return "Inventario"; }
    @Override public String externo() { return "Proveedores Externos"; }
    @Override public Map<String, String> mapeo() { return MAPEO; }
}
