using System.Text.Json;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Transversal;

/// <summary>Convierte el cuerpo JSON de una petición en un diccionario de valores simples (adaptador de entrada).</summary>
public static class Valores
{
    public static Dictionary<string, object?> DesdeJson(Dictionary<string, JsonElement>? cuerpo) =>
        (cuerpo ?? new()).ToDictionary(kv => kv.Key, kv => Normalizar(kv.Value));

    public static object? Normalizar(JsonElement e) => e.ValueKind switch
    {
        JsonValueKind.String => e.GetString(),
        JsonValueKind.Number => e.TryGetInt64(out var l) ? l : e.GetDouble(),
        JsonValueKind.True => true,
        JsonValueKind.False => false,
        JsonValueKind.Null or JsonValueKind.Undefined => null,
        _ => e.GetRawText(),
    };
}
