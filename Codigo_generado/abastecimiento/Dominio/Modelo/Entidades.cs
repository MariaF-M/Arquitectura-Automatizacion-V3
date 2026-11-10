namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;

/// <summary>Entidad «Medicamento» del contexto Abastecimiento (Data Object en V8).</summary>
public class Medicamento
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string? Codigo { get; set; }
    public string? PrincipioActivo { get; set; }
}

/// <summary>Entidad «Requerimiento de compra» del contexto Abastecimiento (Data Object en V8).</summary>
public class RequerimientoDeCompra
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string? PrincipioActivo { get; set; }
    public int? Cantidad { get; set; }
}

/// <summary>Entidad «Autorización técnica» del contexto Abastecimiento (Data Object en V8).</summary>
public class AutorizacionTecnica
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string? AutorizadoPor { get; set; }
    public DateOnly? Fecha { get; set; }
}
