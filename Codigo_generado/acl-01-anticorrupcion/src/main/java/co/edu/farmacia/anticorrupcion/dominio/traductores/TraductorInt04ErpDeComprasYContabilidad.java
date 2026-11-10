package co.edu.farmacia.anticorrupcion.dominio.traductores;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * INT-04 ERP de compras y contabilidad (salida).
 * Abastecimiento --evento «Requerimiento Autorizado»--> ACL-01 --«OBJ-04 — Requerimiento y estado de compra»--> Sistema ERP (Compras)
 */
public class TraductorInt04ErpDeComprasYContabilidad implements Traductor {
    private static final Map<String, String> MAPEO = new LinkedHashMap<>();
    static {
        MAPEO.put("principio_activo", "dci");
        MAPEO.put("concentracion", "concentracion");
        MAPEO.put("cantidad", "cantidad_solicitada");
        MAPEO.put("nivel_urgencia", "prioridad");
    }

    @Override public String codigo() { return "INT-04"; }
    @Override public String nombre() { return "ERP de compras y contabilidad"; }
    @Override public String direccion() { return "salida"; }
    @Override public String contexto() { return "Abastecimiento"; }
    @Override public String externo() { return "Sistema ERP (Compras)"; }
    @Override public Map<String, String> mapeo() { return MAPEO; }
}
