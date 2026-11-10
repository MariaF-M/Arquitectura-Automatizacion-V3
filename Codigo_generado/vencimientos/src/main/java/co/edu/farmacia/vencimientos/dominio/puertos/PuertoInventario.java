package co.edu.farmacia.vencimientos.dominio.puertos;

/** Vencimientos consume a Inventario — «Shared Kernel (núcleo compartido: Lote)» (shared-kernel). */
public interface PuertoInventario {
    Object consultar(String ruta);
}
