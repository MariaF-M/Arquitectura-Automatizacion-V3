using System.Text.Json;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Entrada;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Servicios;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Transversal;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Entrada;

/// <summary>
/// API HTTP de Abastecimiento (adaptador de entrada), generada desde el modelo.
/// POST /requerimiento-compra/generar-requisicion ← «Generar Requisición»
/// POST /requerimiento-compra/{id}/autorizar-requisicion ← «Autorizar Requisición»
/// </summary>
public static class Rutas
{
    private static IResult Ejecutar(Func<object?> accion, int codigo = 200)
    {
        try { return Results.Json(accion(), statusCode: codigo); }
        catch (ReglaNegocioException e) { return Results.Json(new { error = e.Message }, statusCode: 422); }
        catch (NoEncontradoException e) { return Results.Json(new { error = e.Message }, statusCode: 404); }
        catch (CasoDeUsoPendienteException e) { return Results.Json(new { error = e.Message }, statusCode: 501); }
        catch (Exception e)
        {
            // Último recurso: nunca se devuelve una página de error ni se filtran detalles; el detalle va al log
            Console.Error.WriteLine($"[error inesperado] {e}");
            return Results.Json(new { error = "Error interno del servidor. El detalle quedó en el log del servicio." }, statusCode: 500);
        }
    }

    /// <summary>Lee el cuerpo como JSON sin exigir el encabezado Content-Type (igual que los servicios Python y Java).</summary>
    private static async Task<Dictionary<string, object?>?> Cuerpo(HttpRequest req)
    {
        using var lector = new StreamReader(req.Body);
        var texto = await lector.ReadToEndAsync();
        if (string.IsNullOrWhiteSpace(texto)) return new();
        try { return Valores.DesdeJson(JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(texto)); }
        catch (JsonException) { return null; }
    }

    private static async Task<IResult> ConCuerpo(HttpRequest req, Func<Dictionary<string, object?>, object?> accion, int codigo = 201)
    {
        var cuerpo = await Cuerpo(req);
        return cuerpo is null ? Results.Json(new { error = "El cuerpo de la petición no es un objeto JSON válido" }, statusCode: 400) : Ejecutar(() => accion(cuerpo), codigo);
    }

    public static void Mapear(WebApplication app, Func<object> arquitectura)
    {
        app.MapGet("/salud", () => Results.Json(new Dictionary<string, object?> { ["contexto"] = "Abastecimiento", ["estado"] = "ok" }));
        app.MapGet("/eventos", (BusEventos bus) => Results.Json(bus.Historial));
        app.MapGet("/arquitectura", () => Results.Json(arquitectura()));
        app.MapPost("/funciones/{funcion}", (string funcion, HttpRequest req) =>
            Catalogo.Funciones.TryGetValue(funcion, out var f)
                ? ConCuerpo(req, d => f(d))
                : Task.FromResult(Results.Json(new { error = $"Función {funcion} no existe" }, statusCode: 404)));

        app.MapGet("/requerimiento-compra", (ManejadorRequerimientoCompra m) => Ejecutar(() => m.Listar()));
        app.MapGet("/requerimiento-compra/{id}", (string id, ManejadorRequerimientoCompra m) => Ejecutar(() => m.Obtener(id)));
        app.MapPost("/requerimiento-compra/{id}/deshacer", (string id, ManejadorRequerimientoCompra m) => Ejecutar(() => m.Deshacer(id), 201));
        app.MapPost("/requerimiento-compra/generar-requisicion", (HttpRequest req, ManejadorRequerimientoCompra m) =>
            ConCuerpo(req, d => m.Manejar(new GenerarRequisicionComando(d))));
        app.MapPost("/requerimiento-compra/{id}/autorizar-requisicion", (string id, HttpRequest req, ManejadorRequerimientoCompra m) =>
            ConCuerpo(req, d => m.Manejar(new AutorizarRequisicionComando(id, d))));
    }
}
