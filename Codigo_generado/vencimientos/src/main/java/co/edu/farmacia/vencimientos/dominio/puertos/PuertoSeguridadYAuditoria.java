package co.edu.farmacia.vencimientos.dominio.puertos;

/** Vencimientos consume a Seguridad y Auditoría — «Open Host Service» (open-host-service). */
public interface PuertoSeguridadYAuditoria {
    Object consultar(String ruta);
}
