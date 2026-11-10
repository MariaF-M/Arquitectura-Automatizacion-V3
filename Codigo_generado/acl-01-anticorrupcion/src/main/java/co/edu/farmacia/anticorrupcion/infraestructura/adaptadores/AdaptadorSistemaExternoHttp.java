package co.edu.farmacia.anticorrupcion.infraestructura.adaptadores;

import co.edu.farmacia.anticorrupcion.dominio.puertos.PuertoSistemaExterno;
import co.edu.farmacia.anticorrupcion.infraestructura.transversal.Json;

import java.util.Map;
import java.util.logging.Logger;

/**
 * Envía al sistema externo. La URL sale de EXT_INT_0X_URL; si no está configurada, el envío se
 * simula y se registra en el log (útil mientras no exista el sistema real).
 * Externos (V8): Programación Quirúrgica, Historia Clínica (HCE), Servicio de Urgencias, Sistema ERP (Compras), Proveedores Externos, INVIMA (Vigilancia).
 */
public class AdaptadorSistemaExternoHttp implements PuertoSistemaExterno {
    private static final Logger LOG = Logger.getLogger("externos");
    private final ClienteHttp http = new ClienteHttp();

    @Override
    public Object enviar(String codigo, String externo, Map<String, Object> datos) {
        String url = System.getenv("EXT_" + codigo.replace('-', '_') + "_URL");
        if (url == null || url.isBlank()) {
            LOG.info("[simulado] " + codigo + " -> " + externo + ": " + Json.escribir(datos));
            return Map.of("simulado", true, "externo", externo, "enviado", datos);
        }
        return http.post(url, datos);
    }
}
