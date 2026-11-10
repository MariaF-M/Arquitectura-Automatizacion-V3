namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;

/// <summary>Se viola una invariante del agregado (V6 + spec.yaml).</summary>
public class ReglaNegocioException(string mensaje) : Exception(mensaje);

/// <summary>El agregado solicitado no existe.</summary>
public class NoEncontradoException(string mensaje) : Exception(mensaje);
