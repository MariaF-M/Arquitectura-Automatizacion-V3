namespace Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;

/// <summary>Abastecimiento consume a Planificación de Demanda — «Customer / Supplier» (customer-supplier).</summary>
public interface IPuertoPlanificacionDeDemanda
{
    Task<string> Consultar(string ruta);
}

/// <summary>Abastecimiento consume a Seguridad y Auditoría — «Open Host Service» (open-host-service).</summary>
public interface IPuertoSeguridadYAuditoria
{
    Task<string> Consultar(string ruta);
}

/// <summary>Abastecimiento consume a Inventario — «Customer / Supplier» (customer-supplier).</summary>
public interface IPuertoInventario
{
    Task<string> Consultar(string ruta);
}

/// <summary>Salida hacia sistemas externos, siempre a través de la ACL-01 (V9).</summary>
public interface IPuertoAnticorrupcion
{
    Task Enviar(string codigoIntegracion, Dictionary<string, object?> datos);
}
