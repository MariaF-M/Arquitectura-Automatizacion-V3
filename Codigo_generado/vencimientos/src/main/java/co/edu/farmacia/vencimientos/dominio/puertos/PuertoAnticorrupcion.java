package co.edu.farmacia.vencimientos.dominio.puertos;

import java.util.Map;

/** Salida hacia sistemas externos, siempre a través de la ACL-01 (V9). */
public interface PuertoAnticorrupcion {
    void enviar(String codigoIntegracion, Map<String, Object> datos);
}
