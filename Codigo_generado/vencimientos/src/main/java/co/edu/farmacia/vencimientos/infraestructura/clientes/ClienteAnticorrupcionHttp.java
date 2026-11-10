package co.edu.farmacia.vencimientos.infraestructura.clientes;

import co.edu.farmacia.vencimientos.dominio.puertos.PuertoAnticorrupcion;

import java.util.Map;
import java.util.logging.Logger;

/** Envía datos a la ACL-01, que los traduce al formato del sistema externo. */
public class ClienteAnticorrupcionHttp implements PuertoAnticorrupcion {
    private static final Logger LOG = Logger.getLogger("acl");
    private final ClienteHttp http;

    public ClienteAnticorrupcionHttp(ClienteHttp http) { this.http = http; }

    @Override
    public void enviar(String codigo, Map<String, Object> datos) {
        try { http.post("/salientes/" + codigo.toLowerCase(), datos); }
        catch (RuntimeException e) { LOG.warning("ACL no disponible para " + codigo + ": " + e.getMessage()); }
    }
}
