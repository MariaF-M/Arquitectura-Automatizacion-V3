package co.edu.farmacia.vencimientos.dominio.modelo;

import java.time.LocalDate;
import java.util.UUID;

/**
 * Entidad «Restricción de uso» del contexto Vencimientos (Data Object en V8).
 */
public class RestriccionDeUso {
    private String id = UUID.randomUUID().toString();
    private String loteCodigo;
    private String motivo;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getLoteCodigo() { return loteCodigo; }
    public void setLoteCodigo(String loteCodigo) { this.loteCodigo = loteCodigo; }
    public String getMotivo() { return motivo; }
    public void setMotivo(String motivo) { this.motivo = motivo; }
}
