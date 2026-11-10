package co.edu.farmacia.vencimientos.dominio.modelo;

/** Se viola una invariante del agregado. */
public class ReglaNegocioException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public ReglaNegocioException(String mensaje) { super(mensaje); }
}
