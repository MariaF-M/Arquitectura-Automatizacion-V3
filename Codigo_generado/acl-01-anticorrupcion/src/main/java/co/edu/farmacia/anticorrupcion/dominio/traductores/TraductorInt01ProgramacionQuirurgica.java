package co.edu.farmacia.anticorrupcion.dominio.traductores;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * INT-01 Programación quirúrgica (entrada).
 * Programación Quirúrgica --«OBJ-01 — Agenda quirúrgica confirmada»--> ACL-01 --comando «Calcular Demanda»--> Planificación de Demanda
 */
public class TraductorInt01ProgramacionQuirurgica implements Traductor {
    private static final Map<String, String> MAPEO = new LinkedHashMap<>();
    static {
        MAPEO.put("medicamento_requerido", "medicamento");
        MAPEO.put("fecha_programada", "periodo");
        MAPEO.put("unidades_por_procedimiento", "demanda_programada");
    }
    /** Variable de entorno con la URL del contexto destino. */
    public static final String VARIABLE_URL = "PLANIFICACION_DE_DEMANDA_URL";
    public static final String URL_DEFECTO = "http://localhost:8003";
    /** Ruta del comando en el contexto destino ({id} se toma del campo traducido "id"). */
    public static final String RUTA_COMANDO = "/estimacion-demanda/calcular-demanda";

    @Override public String codigo() { return "INT-01"; }
    @Override public String nombre() { return "Programación quirúrgica"; }
    @Override public String direccion() { return "entrada"; }
    @Override public String contexto() { return "Planificación de Demanda"; }
    @Override public String externo() { return "Programación Quirúrgica"; }
    @Override public Map<String, String> mapeo() { return MAPEO; }
}
