namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Servicios;

/// <summary>La función existe en el diagrama pero su lógica aún no se implementa.</summary>
public class CasoDeUsoPendienteException(string mensaje) : Exception(mensaje);

/// <summary>Application Function «Seguimiento del abastecimiento» (V5).</summary>
public class SeguimientoDelAbastecimiento
{
    public Dictionary<string, object?> Ejecutar(Dictionary<string, object?> datos) =>
        throw new CasoDeUsoPendienteException("«Seguimiento del abastecimiento» está modelada pero su lógica está pendiente");
}

/// <summary>Application Function «Cálculo de cantidad requerida» (V5).</summary>
public class CalculoDeCantidadRequerida
{
    public Dictionary<string, object?> Ejecutar(Dictionary<string, object?> datos) =>
        throw new CasoDeUsoPendienteException("«Cálculo de cantidad requerida» está modelada pero su lógica está pendiente");
}

/// <summary>Application Component «Gestión de requerimientos de compra» (V5).</summary>
public class GestionDeRequerimientosDeCompraServicio
{
    public const string Nombre = "Gestión de requerimientos de compra";
}

/// <summary>Application Component «Gestión de autorización técnica» (V5).</summary>
public class GestionDeAutorizacionTecnicaServicio
{
    public const string Nombre = "Gestión de autorización técnica";
}

public static class Catalogo
{
    public static readonly string[] Componentes = [GestionDeRequerimientosDeCompraServicio.Nombre, GestionDeAutorizacionTecnicaServicio.Nombre];

    public static readonly Dictionary<string, Func<Dictionary<string, object?>, Dictionary<string, object?>>> Funciones = new()
    {
        ["seguimiento-del-abastecimiento"] = d => new SeguimientoDelAbastecimiento().Ejecutar(d),
        ["calculo-de-cantidad-requerida"] = d => new CalculoDeCantidadRequerida().Ejecutar(d),
    };
}
