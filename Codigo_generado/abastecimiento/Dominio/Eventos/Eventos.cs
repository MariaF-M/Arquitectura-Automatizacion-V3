namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;

/// <summary>Base de los eventos de dominio de Abastecimiento (Application Events de V6).</summary>
public abstract class EventoDominio(string agregadoId, Dictionary<string, object?> datos)
{
    public string AgregadoId { get; } = agregadoId;
    public Dictionary<string, object?> Datos { get; } = datos;
    public string OcurridoEn { get; } = DateTimeOffset.UtcNow.ToString("o");
    public string Nombre => GetType().Name;

    public Dictionary<string, object?> AMapa() => new()
    {
        ["evento"] = Nombre, ["agregado_id"] = AgregadoId, ["datos"] = Datos, ["ocurrido_en"] = OcurridoEn,
    };
}

/// <summary>Evento «Requisición Sugerida» del agregado RequerimientoCompra.</summary>
public class RequisicionSugerida(string agregadoId, Dictionary<string, object?> datos) : EventoDominio(agregadoId, datos);

/// <summary>Evento «Requerimiento Autorizado» del agregado RequerimientoCompra.</summary>
public class RequerimientoAutorizado(string agregadoId, Dictionary<string, object?> datos) : EventoDominio(agregadoId, datos);
