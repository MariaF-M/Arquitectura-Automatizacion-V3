package co.edu.farmacia.vencimientos.infraestructura.clientes;

import co.edu.farmacia.vencimientos.dominio.puertos.PuertoSeguridadYAuditoria;

/** Adaptador HTTP hacia Seguridad y Auditoría (open-host-service). */
public class ClienteSeguridadYAuditoriaHttp implements PuertoSeguridadYAuditoria {
    private final ClienteHttp http;

    public ClienteSeguridadYAuditoriaHttp(ClienteHttp http) { this.http = http; }

    @Override
    public Object consultar(String ruta) { return http.get(ruta); }
}
