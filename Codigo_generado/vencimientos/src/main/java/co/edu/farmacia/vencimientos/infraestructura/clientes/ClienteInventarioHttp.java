package co.edu.farmacia.vencimientos.infraestructura.clientes;

import co.edu.farmacia.vencimientos.dominio.puertos.PuertoInventario;

/** Adaptador HTTP hacia Inventario (shared-kernel). */
public class ClienteInventarioHttp implements PuertoInventario {
    private final ClienteHttp http;

    public ClienteInventarioHttp(ClienteHttp http) { this.http = http; }

    @Override
    public Object consultar(String ruta) { return http.get(ruta); }
}
