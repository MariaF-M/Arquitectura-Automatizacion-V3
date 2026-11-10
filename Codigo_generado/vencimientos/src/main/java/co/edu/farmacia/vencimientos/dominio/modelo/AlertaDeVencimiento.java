package co.edu.farmacia.vencimientos.dominio.modelo;

import java.time.LocalDate;
import java.util.UUID;

/**
 * Entidad «Alerta de vencimiento» del contexto Vencimientos (Data Object en V8).
 */
public class AlertaDeVencimiento {
    private String id = UUID.randomUUID().toString();
    private String loteCodigo;
    private String semaforo;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getLoteCodigo() { return loteCodigo; }
    public void setLoteCodigo(String loteCodigo) { this.loteCodigo = loteCodigo; }
    public String getSemaforo() { return semaforo; }
    public void setSemaforo(String semaforo) { this.semaforo = semaforo; }
}
