package co.edu.farmacia.vencimientos.sharedkernel;

import java.time.LocalDate;
import java.util.UUID;

/**
 * Shared Kernel «Lote» (V8). Contrato canónico: contratos/shared-kernel/lote.schema.json.
 * Cualquier cambio se acuerda con el otro contexto que lo comparte.
 */
public class Lote {
    private String id = UUID.randomUUID().toString();
    private String codigo;
    private LocalDate fechaVencimiento;
    private String estado;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCodigo() { return codigo; }
    public void setCodigo(String codigo) { this.codigo = codigo; }
    public LocalDate getFechaVencimiento() { return fechaVencimiento; }
    public void setFechaVencimiento(LocalDate fechaVencimiento) { this.fechaVencimiento = fechaVencimiento; }
    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }
}
