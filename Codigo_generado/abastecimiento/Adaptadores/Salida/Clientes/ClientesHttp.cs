using System.Net.Http.Json;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Clientes;

/// <summary>Adaptador HTTP hacia Planificación de Demanda (customer-supplier).</summary>
public class ClientePlanificacionDeDemandaHttp(HttpClient http) : IPuertoPlanificacionDeDemanda
{
    public Task<string> Consultar(string ruta) => http.GetStringAsync(ruta);
}

/// <summary>Adaptador HTTP hacia Seguridad y Auditoría (open-host-service).</summary>
public class ClienteSeguridadYAuditoriaHttp(HttpClient http) : IPuertoSeguridadYAuditoria
{
    public Task<string> Consultar(string ruta) => http.GetStringAsync(ruta);
}

/// <summary>Adaptador HTTP hacia Inventario (customer-supplier).</summary>
public class ClienteInventarioHttp(HttpClient http) : IPuertoInventario
{
    public Task<string> Consultar(string ruta) => http.GetStringAsync(ruta);
}

/// <summary>Envía datos a la ACL-01, que los traduce al formato del sistema externo.</summary>
public class ClienteAnticorrupcionHttp(HttpClient http, ILogger<ClienteAnticorrupcionHttp> log) : IPuertoAnticorrupcion
{
    public async Task Enviar(string codigo, Dictionary<string, object?> datos)
    {
        try { (await http.PostAsJsonAsync($"/salientes/{codigo.ToLowerInvariant()}", datos)).EnsureSuccessStatusCode(); }
        catch (Exception e) { log.LogWarning("ACL no disponible para {Codigo}: {Error}", codigo, e.Message); }
    }
}
