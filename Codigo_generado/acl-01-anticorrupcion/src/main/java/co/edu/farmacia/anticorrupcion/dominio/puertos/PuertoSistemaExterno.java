package co.edu.farmacia.anticorrupcion.dominio.puertos;

import java.util.Map;

/** Puerto de salida de la ACL hacia los sistemas externos, en el formato del externo. */
public interface PuertoSistemaExterno {
    Object enviar(String codigo, String externo, Map<String, Object> datos);
}
