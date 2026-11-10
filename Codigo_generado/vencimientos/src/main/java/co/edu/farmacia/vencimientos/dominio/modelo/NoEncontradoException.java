package co.edu.farmacia.vencimientos.dominio.modelo;

/** El agregado solicitado no existe. */
public class NoEncontradoException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public NoEncontradoException(String mensaje) { super(mensaje); }
}
