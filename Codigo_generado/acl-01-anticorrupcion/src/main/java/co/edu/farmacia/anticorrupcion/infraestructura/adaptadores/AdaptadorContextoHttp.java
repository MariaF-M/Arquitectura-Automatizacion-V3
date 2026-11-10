package co.edu.farmacia.anticorrupcion.infraestructura.adaptadores;

import co.edu.farmacia.anticorrupcion.dominio.puertos.PuertoContextoInterno;

import java.util.Map;

/** Invoca por HTTP el comando del contexto interno. */
public class AdaptadorContextoHttp implements PuertoContextoInterno {
    private final ClienteHttp http = new ClienteHttp();

    @Override
    public Object ejecutarComando(String urlBase, String ruta, Map<String, Object> datos) {
        return http.post(urlBase + ruta, datos);
    }
}
